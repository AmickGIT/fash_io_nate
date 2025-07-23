#Autoencoder

import pandas as pd
import numpy as np
from sklearn.preprocessing import OneHotEncoder
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader

df = pd.read_csv("data.csv")
id_to_index = {row['img']: idx for idx, row in df.iterrows()}


attributes = ['sleeve', 'neck', 'fit', 'primary_color']

encoder = OneHotEncoder()
encoded = encoder.fit_transform(df[attributes]).toarray()

class FashionDataset(Dataset):
    def __init__(self, X):
        self.X = torch.tensor(X, dtype=torch.float32)

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        return self.X[idx]

dataset = FashionDataset(encoded)
loader = DataLoader(dataset, batch_size=32, shuffle=True)

class FashionAutoencoder(nn.Module):
    def __init__(self, input_dim, latent_dim=16):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 64),
            nn.ReLU(),
            nn.Linear(64, latent_dim)
        )
        self.decoder = nn.Sequential(
            nn.Linear(latent_dim, 64),
            nn.ReLU(),
            nn.Linear(64, input_dim),
            nn.Sigmoid()
        )

    def forward(self, x):
        latent = self.encoder(x)
        recon = self.decoder(latent)
        return recon, latent

input_dim = encoded.shape[1]
model = FashionAutoencoder(input_dim)
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
loss_fn = nn.MSELoss()

for epoch in range(50):
    model.train()
    total_loss = 0
    for batch in loader:
        recon, _ = model(batch)
        loss = loss_fn(recon, batch)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        total_loss += loss.item()
    print(f"Epoch {epoch+1}: Loss = {total_loss:.4f}")


id1 = "00012_00.jpg"
id2 = "00026_00.jpg"

index1 = id_to_index[id1]
index2 = id_to_index[id2]

input1 = torch.tensor(encoded[index1], dtype=torch.float32).unsqueeze(0)
input2 = torch.tensor(encoded[index2], dtype=torch.float32).unsqueeze(0)
model.eval()
_, latent1 = model(input1)
_, latent2 = model(input2)

mixed_latent = (latent1 + latent2) / 2

new_design_vector = model.decoder(mixed_latent).detach().numpy()[0]

decoded_attributes = encoder.inverse_transform([new_design_vector])
print("\nNew Garment Design (Mixed):")
print(decoded_attributes[0])
