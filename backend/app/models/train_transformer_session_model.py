
# transformer_session_model.py

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from datetime import timedelta
import sqlite3
from dotenv import load_dotenv
from pathlib import Path

DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'

# ------------------------
# Dataset & Preprocessing
# ------------------------

dotenv_path = Path(__file__).parents[3] / '.env'
load_dotenv(dotenv_path=dotenv_path)

class LogSessionDataset(Dataset):
    def __init__(self, session_length=5):
        project_root = Path(__file__).parents[3]
        db_file = project_root / 'data' / 'user_logs.db'
        print(f"Loading data from: {db_file}")
        conn = sqlite3.connect(db_file)
        df = pd.read_sql_query("SELECT * FROM user_logs ORDER BY user_id, timestamp", conn)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        self.sessions = []
        self.labels = []
        self.user_ids = []
        self.session_logs = []  # ✅ NEW: store logs alongside sessions

        cat_cols = ['action_type', 'resource', 'location', 'device']
        self.label_encoders = {}
        for col in cat_cols:
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col])
            self.label_encoders[col] = le

        grouped = df.groupby('user_id')
        print(f"Total users: {len(grouped)}")

        for user_id, group in grouped:
            logs = group.sort_values('timestamp').reset_index(drop=True)
            session = []
            session_labels = []
            for idx, row in logs.iterrows():
                features = [
                    int(row['hour_of_day']),
                    int(row['num_files_accessed']),
                    int(row['action_type']),
                    int(row['resource']),
                    int(row['location']),
                    int(row['device']),
                ]
                session.append(features)
                session_labels.append(int(row['is_synthetic_anomaly']))

                if len(session) == session_length:
                    self.sessions.append(session.copy())
                    self.labels.append(1 if sum(session_labels) > 0 else 0)
                    self.user_ids.append(user_id)
                    session_logs = logs.iloc[idx - session_length + 1: idx + 1].copy()

                    # Convert timestamps to string
                    session_logs['timestamp'] = session_logs['timestamp'].apply(lambda x: x.isoformat())

                    self.session_logs.append(session_logs.to_dict(orient='records'))

                    session = []
                    session_labels = []

            # If leftover partial session at end (optional: only if full session)
            if len(session) == session_length:
                self.sessions.append(session.copy())
                self.labels.append(1 if sum(session_labels) > 0 else 0)
                self.user_ids.append(user_id)
                self.session_logs.append(
                    logs.iloc[-session_length:].to_dict(orient='records')
                )

    def __len__(self):
        return len(self.sessions)

    def __getitem__(self, idx):
        x = torch.tensor(self.sessions[idx], dtype=torch.float32)
        y = torch.tensor(self.labels[idx], dtype=torch.float32)
        user_id = self.user_ids[idx]
        logs = self.session_logs[idx]
        return x, y, user_id, logs




# ------------------------
# Transformer Model
# ------------------------

class SessionTransformer(nn.Module):
    def __init__(self, input_dim, d_model=64, nhead=4, num_layers=2):
        super(SessionTransformer, self).__init__()
        self.embedding = nn.Linear(input_dim, d_model)
        encoder_layer = nn.TransformerEncoderLayer(d_model=d_model, nhead=nhead, batch_first=True)
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        self.fc = nn.Linear(d_model, 1)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        x = self.embedding(x)
        x = self.transformer(x)
        x = x.mean(dim=1)
        x = self.fc(x)
        return self.sigmoid(x).squeeze()

# ------------------------
# Training Loop
# ------------------------

def train_model():
    db_file = str(Path(__file__).parents[2] / 'data' / 'user_logs.db')
    dataset = LogSessionDataset(session_length=5)
    print("Dataset size:", len(dataset))
    dataloader = DataLoader(dataset, batch_size=32, shuffle=True)

    model = SessionTransformer(input_dim=6).to(DEVICE)
    criterion = nn.BCELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)

    for epoch in range(10):
        model.train()
        total_loss = 0
        for x, y, _, _ in dataloader:
            x, y = x.to(DEVICE), y.to(DEVICE)
            optimizer.zero_grad()
            output = model(x)
            loss = criterion(output, y)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        print(f"Epoch {epoch+1} Loss: {total_loss:.4f}")

    torch.save(model.state_dict(), "session_transformer.pt")

if __name__ == '__main__':
    train_model()
