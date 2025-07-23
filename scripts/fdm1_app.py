#Fashion deisgner model 1 - streamlit
import streamlit as st
import pandas as pd
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from sklearn.preprocessing import OneHotEncoder

st.title("AI Fashion Designer – Garment Attribute Mixer")

uploaded_file = st.file_uploader("Upload your `data.csv` with garment attributes", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.success("CSV uploaded successfully!")

    attributes = ['sleeve', 'neck', 'fit', 'primary_color']
    encoder = OneHotEncoder()
    encoded = encoder.fit_transform(df[attributes]).toarray()

    id_to_index = {row['img']: idx for idx, row in df.iterrows()}
    index_to_id = {v: k for k, v in id_to_index.items()}

    class FashionDataset(Dataset):
        def __init__(self, X):
            self.X = torch.tensor(X, dtype=torch.float32)

        def __len__(self):
            return len(self.X)

        def __getitem__(self, idx):
            return self.X[idx]

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

    with st.spinner("Training model..."):
        dataset = FashionDataset(encoded)
        loader = DataLoader(dataset, batch_size=32, shuffle=True)

        input_dim = encoded.shape[1]
        model = FashionAutoencoder(input_dim)
        optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
        loss_fn = nn.MSELoss()

        for epoch in range(20):
            model.train()
            for batch in loader:
                recon, _ = model(batch)
                loss = loss_fn(recon, batch)

                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

    st.success("Model trained!")

    st.markdown("### Choose Two Garments to Mix")
    col1, col2 = st.columns(2)
    with col1:
        id1 = st.selectbox("Garment 1", df['img'].tolist())
    with col2:
        id2 = st.selectbox("Garment 2", df['img'].tolist(), index=1)

    if st.button("Generate New Design"):
        try:
            index1 = id_to_index[id1]
            index2 = id_to_index[id2]

            input1 = torch.tensor(encoded[index1], dtype=torch.float32).unsqueeze(0)
            input2 = torch.tensor(encoded[index2], dtype=torch.float32).unsqueeze(0)
            model.eval()
            _, latent1 = model(input1)
            _, latent2 = model(input2)

            mixed_latent = (latent1 + latent2) / 2
            new_design_vector = model.decoder(mixed_latent).detach().numpy()[0]

            decoded_attributes = encoder.inverse_transform([new_design_vector])[0]
            st.markdown("### Generated Garment Design (Mixed Attributes)")
            st.write({
                attr: val for attr, val in zip(attributes, decoded_attributes)
            })

        except Exception as e:
            st.error(f"Error: {e}")
