import torch
import torch.nn as nn
from torch.nn import functional as F
import argparse
import os
import time
from cp_dataset import CPDataset, CPDataLoader
from cp_dataset_test import CPDatasetTest
from networks import ConditionGenerator, VGGLoss, load_checkpoint, save_checkpoint, make_grid, make_grid_3d
from network_generator import SPADEGenerator, MultiscaleDiscriminator, GANLoss, Projected_GANs_Loss, set_requires_grad
from sync_batchnorm import DataParallelWithCallback
from utils import create_network
import numpy as np
from torch.utils.data import Subset
from torchvision.transforms import transforms
import eval_models as models
import kornia as tgm
from pg_modules.discriminator import ProjectedDiscriminator
import cv2
from tqdm import tqdm

def remove_overlap(seg_out, warped_cm):
    assert len(warped_cm.shape) == 4
    warped_cm = warped_cm - (torch.cat([seg_out[:, 1:3, :, :], seg_out[:, 5:, :, :]], dim=1)).sum(dim=1, keepdim=True) * warped_cm
    return warped_cm

def freeze_generator_final_blocks(generator, num_unfrozen=2):
    param_blocks = []
    for name, block in generator.named_children():
        if any(p.requires_grad for p in block.parameters(recurse=True)):
            param_blocks.append((name, block))
    for param in generator.parameters():
        param.requires_grad = False
    for name, block in param_blocks[-num_unfrozen:]:
        for param in block.parameters():
            param.requires_grad = True
        print(f"Unfrozen block: {name}")
    unfrozen_names = [name for name, _ in param_blocks[-num_unfrozen:]]
    print("Unfrozen generator blocks for finetuning:", unfrozen_names)

def get_opt():
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', type=str, required=True)
    parser.add_argument('--gpu_ids', type=str, default='0')
    parser.add_argument('-j', '--workers', type=int, default=2)
    parser.add_argument('-b', '--batch_size', type=int, default=2)
    parser.add_argument('--fp16', action='store_true', help='use amp')
    parser.add_argument("--dataroot", default="./data/")
    parser.add_argument("--datamode", default="train")
    parser.add_argument("--data_list", default="train_pairs.txt")
    parser.add_argument("--fine_width", type=int, default=768)
    parser.add_argument("--fine_height", type=int, default=1024)
    parser.add_argument("--radius", type=int, default=20)
    parser.add_argument("--grid_size", type=int, default=5)
    parser.add_argument('--checkpoint_dir', type=str, default='checkpoints', help='save checkpoint infos')
    parser.add_argument('--tocg_checkpoint', type=str, required=True, help='condition generator checkpoint')
    parser.add_argument('--gen_checkpoint', type=str, default='', help='gen checkpoint')
    parser.add_argument('--dis_checkpoint', type=str, default='', help='dis checkpoint')
    parser.add_argument("--display_count", type=int, default=100)
    parser.add_argument("--save_count", type=int, default=10000)
    parser.add_argument("--load_step", type=int, default=0)
    parser.add_argument("--keep_step", type=int, default=100000)
    parser.add_argument("--decay_step", type=int, default=100000)
    parser.add_argument("--shuffle", action='store_true', help='shuffle input data')
    parser.add_argument("--lpips_count", type=int, default=1000)
    parser.add_argument("--test_datasetting", default="paired")
    parser.add_argument("--test_dataroot", default="./my_data/")
    parser.add_argument("--test_data_list", default="test_pairs.txt")
    parser.add_argument('--G_lr', type=float, default=0.0001, help='initial learning rate for adam')
    parser.add_argument('--D_lr', type=float, default=0.0004, help='initial learning rate for adam')
    parser.add_argument('--GMM_const', type=float, default=None)
    parser.add_argument('--semantic_nc', type=int, default=13, help='# of input label classes without unknown class')
    parser.add_argument('--gen_semantic_nc', type=int, default=7)
    parser.add_argument('--norm_G', type=str, default='spectralaliasinstance')
    parser.add_argument('--norm_D', type=str, default='spectralinstance')
    parser.add_argument('--ngf', type=int, default=64)
    parser.add_argument('--ndf', type=int, default=64)
    parser.add_argument('--num_upsampling_layers', choices=['normal', 'more', 'most'], default='most')
    parser.add_argument('--init_type', type=str, default='xavier')
    parser.add_argument('--init_variance', type=float, default=0.02)
    parser.add_argument('--no_ganFeat_loss', action='store_true')
    parser.add_argument('--lambda_l1', type=float, default=1.0)
    parser.add_argument('--lambda_feat', type=float, default=10.0)
    parser.add_argument('--lambda_vgg', type=float, default=10.0)
    parser.add_argument('--n_layers_D', type=int, default=3)
    parser.add_argument('--netD_subarch', type=str, default='n_layer')
    parser.add_argument('--num_D', type=int, default=2)
    parser.add_argument("--composition_mask", action='store_true')
    parser.add_argument('--occlusion', action='store_true')
    parser.add_argument('--cond_G_ngf', type=int, default=96)
    parser.add_argument("--cond_G_input_width", type=int, default=192)
    parser.add_argument("--cond_G_input_height", type=int, default=256)
    parser.add_argument('--cond_G_num_layers', type=int, default=5)
    parser.add_argument("--warp_feature", choices=['encoder', 'T1'], default="T1")
    parser.add_argument("--out_layer", choices=['relu', 'conv'], default="relu")
    parser.add_argument('--unfreeze_last', type=int, default=2, help="Number of generator layers to finetune")
    opt = parser.parse_args()
    str_ids = opt.gpu_ids.split(',')
    opt.gpu_ids = [int(id) for id in str_ids if int(id) >= 0]
    if len(opt.gpu_ids) > 0:
        torch.cuda.set_device(opt.gpu_ids[0])
    assert len(opt.gpu_ids) == 0 or opt.batch_size % len(opt.gpu_ids) == 0
    return opt

def train(opt, train_loader, test_loader, tocg, generator, discriminator, model):
    tocg.cuda()
    tocg.eval()
    generator.train()
    discriminator.train()
    if not opt.composition_mask and hasattr(discriminator, 'feature_network'):
        discriminator.feature_network.requires_grad_(False)
    discriminator.cuda()
    model.eval()
    criterionL1 = nn.L1Loss()
    criterionFeat = nn.L1Loss()
    criterionVGG = VGGLoss()
    criterionGAN = GANLoss('hinge', tensor=torch.cuda.FloatTensor)

    optimizer_gen = torch.optim.Adam(
        filter(lambda p: p.requires_grad, generator.parameters()),
        lr=opt.G_lr, betas=(0, 0.9)
    )
    optimizer_dis = torch.optim.Adam(discriminator.parameters(), lr=opt.D_lr, betas=(0, 0.9))

    for step in tqdm(range(opt.load_step, opt.keep_step + opt.decay_step)):
        inputs = train_loader.next_batch()
        agnostic = inputs['agnostic'].cuda()
        parse_GT = inputs['parse'].cuda()
        pose = inputs['densepose'].cuda()
        parse_cloth = inputs['parse_cloth'].cuda()
        parse_agnostic = inputs['parse_agnostic'].cuda()
        pcm = inputs['pcm'].cuda()
        cm = inputs['cloth_mask']['paired'].cuda()
        c_paired = inputs['cloth']['paired'].cuda()
        im = inputs['image'].cuda()

        with torch.no_grad():
            pre_clothes_mask_down = F.interpolate(cm, size=(opt.cond_G_input_height, opt.cond_G_input_width), mode='nearest')
            input_parse_agnostic_down = F.interpolate(parse_agnostic, size=(opt.cond_G_input_height, opt.cond_G_input_width), mode='nearest')
            clothes_down = F.interpolate(c_paired, size=(opt.cond_G_input_height, opt.cond_G_input_width), mode='bilinear')
            densepose_down = F.interpolate(pose, size=(opt.cond_G_input_height, opt.cond_G_input_width), mode='bilinear')
            input1 = torch.cat([clothes_down, pre_clothes_mask_down], 1)
            input2 = torch.cat([input_parse_agnostic_down, densepose_down], 1)
            flow_list_taco, fake_segmap, warped_cloth_paired_taco, warped_clothmask_paired_taco, flow_list_tvob, warped_cloth_paired_tvob, warped_clothmask_paired_tvob = tocg(input1, input2)
            warped_clothmask_paired_taco_onehot = torch.FloatTensor((warped_clothmask_paired_taco.detach().cpu().numpy() > 0.5).astype(np.float32)).cuda()
            cloth_mask = torch.ones_like(fake_segmap)
            cloth_mask[:,3:4, :, :] = warped_clothmask_paired_taco
            fake_segmap = fake_segmap * cloth_mask
            N, _, iH, iW = c_paired.shape
            N, flow_iH, flow_iW, _ = flow_list_tvob[-1].shape
            flow_tvob = F.interpolate(flow_list_tvob[-1].permute(0, 3, 1, 2), size=(iH, iW), mode='bilinear').permute(0, 2, 3, 1)
            flow_tvob_norm = torch.cat([flow_tvob[:, :, :, 0:1] / ((flow_iW - 1.0) / 2.0), flow_tvob[:, :, :, 1:2] / ((flow_iH - 1.0) / 2.0)], 3)
            grid = make_grid(N, iH, iW)
            grid_3d = make_grid_3d(N, iH, iW)
            warped_grid_tvob = grid + flow_tvob_norm
            warped_cloth_tvob = F.grid_sample(c_paired, warped_grid_tvob, padding_mode='border')
            warped_clothmask_tvob = F.grid_sample(cm, warped_grid_tvob, padding_mode='border')
            flow_taco = F.interpolate(flow_list_taco[-1].permute(0, 4, 1, 2, 3), size=(2,iH,iW), mode='trilinear').permute(0, 2, 3, 4, 1)
            flow_taco_norm = torch.cat([flow_taco[:, :, :, :, 0:1] / ((flow_iW - 1.0) / 2.0), flow_taco[:, :, :, :, 1:2] / ((flow_iH - 1.0) / 2.0), flow_taco[:, :, :, :, 2:3]], 4)
            warped_cloth_tvob = warped_cloth_tvob.unsqueeze(2)
            warped_cloth_paired_taco = F.grid_sample(torch.cat((warped_cloth_tvob, torch.zeros_like(warped_cloth_tvob).cuda()), dim=2), flow_taco_norm + grid_3d, padding_mode='border')
            warped_cloth_paired_taco = warped_cloth_paired_taco[:,:,0,:,:]
            warped_clothmask_tvob = warped_clothmask_tvob.unsqueeze(2)
            warped_clothmask_taco = F.grid_sample(torch.cat((warped_clothmask_tvob, torch.zeros_like(warped_clothmask_tvob).cuda()), dim=2), flow_taco_norm + grid_3d, padding_mode='border')
            warped_clothmask_taco = warped_clothmask_taco[:,:,0,:,:]
            fake_parse_gauss = F.interpolate(fake_segmap, size=(iH, iW), mode='bilinear')
            fake_parse = fake_parse_gauss.argmax(dim=1)[:, None]
            old_parse = torch.FloatTensor(fake_parse.size(0), 13, opt.fine_height, opt.fine_width).zero_().cuda()
            old_parse.scatter_(1, fake_parse, 1.0)
            labels = {
                0:  ['background',  [0]],
                1:  ['paste',       [2, 4, 7, 8, 9, 10, 11]],
                2:  ['upper',       [3]],
                3:  ['hair',        [1]],
                4:  ['left_arm',    [5]],
                5:  ['right_arm',   [6]],
                6:  ['noise',       [12]]
            }
            parse = torch.FloatTensor(fake_parse.size(0), 7, opt.fine_height, opt.fine_width).zero_().cuda()
            for i in range(len(labels)):
                for label in labels[i][1]:
                    parse[:, i] += old_parse[:, label]
            parse = parse.detach()

        output_paired_rendered, output_paired_comp = generator(torch.cat((agnostic, pose, warped_cloth_paired_taco), dim=1), parse)
        output_paired_comp1 = output_paired_comp * warped_clothmask_taco
        output_paired_comp = parse[:,2:3,:,:] * output_paired_comp1
        output_paired = warped_cloth_paired_taco * output_paired_comp + output_paired_rendered * (1 - output_paired_comp)

        fake_concat = torch.cat((parse, output_paired_rendered), dim=1)
        real_concat = torch.cat((parse, im), dim=1)
        pred = discriminator(torch.cat((fake_concat, real_concat), dim=0))
        pred_fake, pred_real = [], []
        for p in pred:
            pred_fake.append([tensor[:tensor.size(0) // 2] for tensor in p])
            pred_real.append([tensor[tensor.size(0) // 2:] for tensor in p])
        G_losses = {}
        G_losses['GAN'] = criterionGAN(pred_fake, True, for_discriminator=False)
        num_D = len(pred_fake)
        GAN_Feat_loss = torch.cuda.FloatTensor(len(opt.gpu_ids)).zero_()
        for i in range(num_D):
            num_intermediate_outputs = len(pred_fake[i]) - 1
            for j in range(num_intermediate_outputs):
                unweighted_loss = criterionFeat(pred_fake[i][j], pred_real[i][j].detach())
                GAN_Feat_loss += unweighted_loss * opt.lambda_feat / num_D
        G_losses['GAN_Feat'] = GAN_Feat_loss
        G_losses['VGG'] = criterionVGG(output_paired, im) * opt.lambda_vgg + criterionVGG(output_paired_rendered, im) * opt.lambda_vgg
        G_losses['L1'] = criterionL1(output_paired_rendered, im) * opt.lambda_l1 + criterionL1(output_paired, im) * opt.lambda_l1
        G_losses['Composition_Mask'] = torch.mean(torch.abs(1 - output_paired_comp))
        loss_gen = sum(G_losses.values()).mean()

        optimizer_gen.zero_grad()
        loss_gen.backward()
        optimizer_gen.step()

        with torch.no_grad():
            output_paired_rendered, output_comp = generator(torch.cat((agnostic, pose, warped_cloth_paired_taco), dim=1), parse)
            output_comp1 = output_comp * warped_clothmask_taco
            output_comp = parse[:,2:3,:,:] * output_comp1
            output = warped_cloth_paired_taco * output_comp + output_paired_rendered * (1 - output_comp)
            output_comp = output_comp.detach(); output = output.detach()
            output_comp.requires_grad_(); output.requires_grad_()

        fake_concat = torch.cat((parse, output_paired_rendered), dim=1)
        real_concat = torch.cat((parse, im), dim=1)
        pred = discriminator(torch.cat((fake_concat, real_concat), dim=0))
        pred_fake, pred_real = [], []
        for p in pred:
            pred_fake.append([tensor[:tensor.size(0) // 2] for tensor in p])
            pred_real.append([tensor[tensor.size(0) // 2:] for tensor in p])

        D_losses = {}
        D_losses['D_Fake'] = criterionGAN(pred_fake, False, for_discriminator=True)
        D_losses['D_Real'] = criterionGAN(pred_real, True, for_discriminator=True)
        loss_dis = sum(D_losses.values()).mean()

        optimizer_dis.zero_grad()
        loss_dis.backward()
        optimizer_dis.step()

        if (step + 1) % opt.display_count == 0:
            print(f"Step: {step+1}, G_loss: {loss_gen.item():.4f}, D_loss: {loss_dis.item():.4f}")

        if (step + 1) % opt.save_count == 0:
            save_checkpoint(generator, os.path.join(opt.checkpoint_dir, opt.name, f'gen_step_{step+1:06d}.pth'))
            save_checkpoint(discriminator, os.path.join(opt.checkpoint_dir, opt.name, f'dis_step_{step+1:06d}.pth'))

def main():
    opt = get_opt()
    print(opt)
    print("Start to train %s!" % opt.name)
    os.makedirs('sample_fs_toig', exist_ok=True)
    train_dataset = CPDataset(opt)
    train_loader = CPDataLoader(opt, train_dataset)
    opt.batch_size = 1
    opt.dataroot = opt.test_dataroot
    opt.datamode = 'test'
    opt.data_list = opt.test_data_list
    test_dataset = CPDatasetTest(opt)
    test_dataset = Subset(test_dataset, np.arange(500))
    test_loader = CPDataLoader(opt, test_dataset)
    input1_nc = 4
    input2_nc = opt.semantic_nc + 3
    tocg = ConditionGenerator(opt, input1_nc=input1_nc, input2_nc=input2_nc, output_nc=13, ngf=opt.cond_G_ngf, norm_layer=nn.BatchNorm2d, num_layers=opt.cond_G_num_layers)
    load_checkpoint(tocg, opt.tocg_checkpoint)
    generator = SPADEGenerator(opt, 3+3+3)
    generator.print_network()
    if len(opt.gpu_ids) > 0:
        assert(torch.cuda.is_available())
        generator.cuda()
    generator.init_weights(opt.init_type, opt.init_variance)
    if opt.composition_mask:
        discriminator = create_network(MultiscaleDiscriminator, opt)
    else:
        discriminator = ProjectedDiscriminator(interp224=False)
    model = models.PerceptualLoss(model='net-lin',net='alex',use_gpu=True)
    if not opt.gen_checkpoint == '' and os.path.exists(opt.gen_checkpoint):
        load_checkpoint(generator, opt.gen_checkpoint)
        load_checkpoint(discriminator, opt.dis_checkpoint)
    freeze_generator_final_blocks(generator, num_unfrozen=opt.unfreeze_last)
    train(opt, train_loader, test_loader, tocg, generator, discriminator, model)
    save_checkpoint(generator, os.path.join(opt.checkpoint_dir, opt.name, 'gen_model_final.pth'))
    save_checkpoint(discriminator, os.path.join(opt.checkpoint_dir, opt.name, 'dis_model_final.pth'))
    print("Finished training %s!" % opt.name)

if __name__ == "__main__":
    main()
