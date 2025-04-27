# inference_session_transformer.py

import torch
from backend.app.models.train_transformer_session_model import SessionTransformer, LogSessionDataset, DEVICE
from torch.utils.data import DataLoader
from pathlib import Path
import json

def clean_log_entry(entry):
    clean_entry = {}
    for key, value in entry.items():
        if isinstance(value, list) and len(value) == 1:
            # Flatten single-item lists
            value = value[0]
        if isinstance(value, torch.Tensor):
            value = value.item()
        clean_entry[key] = value
    return clean_entry


def run_inference():
    model = SessionTransformer(input_dim=6)

    model_path = Path(__file__).parents[1] / "app" / "models" / "session_transformer.pt"
    model.load_state_dict(torch.load(model_path, map_location=DEVICE))

    model.to(DEVICE)
    model.eval()

    dataset = LogSessionDataset(session_length=5)
    dataloader = DataLoader(dataset, batch_size=1, shuffle=False)

    session_outputs = []

    for idx, (x, y, user_id, logs) in enumerate(dataloader):
        x = x.to(DEVICE)

        score = model(x).item()
        pred_label = int(score > 0.5)
        actual_label = int(y.item())

        cleaned_logs = [clean_log_entry(log) for log in logs]

        session_outputs.append({
            "user_id": user_id,
            "session_index": idx,
            "anomaly_score": round(score, 4),
            "predicted_label": pred_label,
            "true_label": actual_label,
            "logs": cleaned_logs
        })

    output_path = Path(__file__).parents[1] / "app" / "data" / "suspicious_sessions.json"
    with open(output_path, "w") as f:
        json.dump(session_outputs, f, indent=2, default=str)


    print(f"✅ Saved {len(session_outputs)} session scores to suspicious_sessions.json")

    # 🔥 Show Top 5 Suspicious Sessions
    print("\n🔎 Top 5 Suspicious Sessions by Anomaly Score:")
    top_sessions = sorted(session_outputs, key=lambda x: x['anomaly_score'], reverse=True)
    for i, session in enumerate(top_sessions[:5]):
        print(f"#{i+1} | User: {session['user_id']} | Score: {session['anomaly_score']} | True Label: {session['true_label']}")

if __name__ == "__main__":
    run_inference()
