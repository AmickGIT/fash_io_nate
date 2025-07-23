import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
import numpy as np

class ColorDataset(Dataset):
    def __init__(self, csv_path):
        df = pd.read_csv(csv_path)
        self.X = df[['skin_H', 'skin_S', 'skin_V', 'cloth_R', 'cloth_G', 'cloth_B']].values.astype(np.float32)
        self.X[:, 0] /= 180.0  # Normalize Hue
        self.X[:, 1:3] /= 255.0  # Normalize S, V
        self.X[:, 3:] /= 255.0   # Normalize RGB
        self.y = df['label'].values.astype(np.float32)

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        return torch.tensor(self.X[idx]), torch.tensor(self.y[idx])

class CompatibilityANN(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(6, 32),
            nn.ReLU(),
            nn.Linear(32, 16),
            nn.ReLU(),
            nn.Linear(16, 1),
            nn.Sigmoid()
        )

    def forward(self, x):
        return self.net(x)


from sklearn.model_selection import train_test_split
import pandas as pd

# Prepare datasets
df = pd.read_csv("skin_cloth_labeled.csv")
df_train, df_test = train_test_split(df, test_size=0.2, random_state=42)

# Save split
df_train.to_csv("train.csv", index=False)
df_test.to_csv("test.csv", index=False)

# Load
train_ds = ColorDataset("train.csv")
test_ds = ColorDataset("test.csv")

train_loader = DataLoader(train_ds, batch_size=16, shuffle=True)
test_loader = DataLoader(test_ds, batch_size=16)

# Train loop
model = CompatibilityANN()
loss_fn = nn.BCELoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

for epoch in range(15):
    model.train()
    total_loss = 0
    for x_batch, y_batch in train_loader:
        y_batch = y_batch.view(-1, 1)
        pred = model(x_batch)
        loss = loss_fn(pred, y_batch)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        total_loss += loss.item()
    print(f"Epoch {epoch+1} - Loss: {total_loss:.3f}")


# Just normalize and save
cloth_df = df[['cloth_R', 'cloth_G', 'cloth_B']].drop_duplicates()
cloth_rgb = cloth_df.values.astype(np.float32) / 255.0
np.save("cloth_color_embeddings.npy", cloth_rgb)
