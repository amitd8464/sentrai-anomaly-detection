
# inference_session_transformer.py

import torch
from backend.app.models.train_transformer_session_model import SessionTransformer, LogSessionDataset, DEVICE
from torch.utils.data import DataLoader
from pathlib import Path
import pandas as pd
import sqlite3
import json

def run_inference():
    model = SessionTransformer(input_dim=6)
    model.load_state_dict(torch.load("session_transformer.pt", map_location=DEVICE))
    model.to(DEVICE)
    model.eval()

    db_file = str(Path(__file__).parents[2] / 'data' / 'user_logs.db')
    dataset = LogSessionDataset(session_length=5)
    dataloader = DataLoader(dataset, batch_size=1, shuffle=False)

    session_outputs = []

    # Load raw logs for attaching later
    conn = sqlite3.connect(db_file)
    df_logs = pd.read_sql_query("SELECT * FROM user_logs ORDER BY user_id, timestamp", conn)
    df_logs['timestamp'] = pd.to_datetime(df_logs['timestamp'])
    grouped = list(df_logs.groupby('user_id'))

    for idx, (x, y) in enumerate(dataloader):
        if idx >= len(grouped):
            break

        x = x.to(DEVICE)
        score = model(x).item()
        pred_label = int(score > 0.5)
        actual_label = int(y.item())

        user_id, group = grouped[idx]
        logs = group.sort_values('timestamp').iloc[idx*5:(idx+1)*5].to_dict(orient='records')

        session_outputs.append({
            "user_id": user_id,
            "session_index": idx,
            "anomaly_score": round(score, 4),
            "predicted_label": pred_label,
            "true_label": actual_label,
            "logs": logs
        })
        print(f"Session {idx} → user {user_id}, score={score:.4f}, label={actual_label}")

    with open("suspicious_sessions.json", "w") as f:
        json.dump(session_outputs, f, indent=2, default=str)

    print(f"✅ Saved {len(session_outputs)} session scores to suspicious_sessions.json")

if __name__ == "__main__":
    run_inference()
