# backend/app/api/anomaly_routes.py

from flask import Blueprint, jsonify, request
import pandas as pd
import torch
from backend.app import db
from backend.app.models.train_transformer_session_model import SessionTransformer, LogSessionDataset, DEVICE
from torch.utils.data import DataLoader
import joblib
from pathlib import Path
import sqlite3

anomaly_bp = Blueprint('anomaly_bp', __name__)

# Load models once
ocsvm_model = joblib.load(Path(__file__).parents[2] / 'app' /'models' / 'anomaly_pipeline.pkl')
transformer_model = SessionTransformer(input_dim=6)
transformer_model.load_state_dict(torch.load(Path(__file__).parents[2] / 'app' / 'models' / 'session_transformer.pt', map_location=DEVICE))
transformer_model.to(DEVICE)
transformer_model.eval()

# Helper to load full logs
def load_user_logs():
    db_file = Path(__file__).parents[2] / 'data' / 'user_logs.db'
    conn = sqlite3.connect(db_file)
    df = pd.read_sql_query("SELECT * FROM user_logs ORDER BY timestamp", conn)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df

@anomaly_bp.route('/logs', methods=['GET'])
def get_all_logs():
    """View all user logs."""
    df = load_user_logs()
    logs = df.to_dict(orient='records')
    return jsonify(logs)

@anomaly_bp.route('/logs/flagged', methods=['GET'])
def get_flagged_logs():
    """View logs flagged by OneClassSVM model."""
    df = load_user_logs()

    # Compute cyclical features
    import numpy as np
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['day_of_week'] = df['timestamp'].dt.dayofweek
    df['hour_cos'] = np.cos(2 * np.pi * df['hour_of_day'] / 24)
    df['hour_sin'] = np.sin(2 * np.pi * df['hour_of_day'] / 24)
    df['dow_cos'] = np.cos(2 * np.pi * df['day_of_week'] / 7)
    df['dow_sin'] = np.sin(2 * np.pi * df['day_of_week'] / 7)

    feature_cols = ['hour_cos', 'hour_sin', 'dow_cos', 'dow_sin', 
                    'hour_of_day', 'num_files_accessed', 'action_type', 'resource', 'location', 'device']

    features = df[feature_cols]

    preds = ocsvm_model.predict(features)

    flagged_logs = df[preds == -1].to_dict(orient='records')
    return jsonify(flagged_logs)

@anomaly_bp.route('/users/suspicious', methods=['GET'])
def get_suspicious_users():
    """View suspicious users based on Transformer model."""
    dataset = LogSessionDataset(session_length=5)
    suspicious_users = set()

    for x, y, user_id, _ in DataLoader(dataset, batch_size=1, shuffle=False):
        x = x.to(DEVICE)
        score = transformer_model(x).item()
        if score > 0.5:
            suspicious_users.add(user_id)

    suspicious_users = list(suspicious_users)
    return jsonify(suspicious_users)

@anomaly_bp.route('/users/<string:user_id>/suspicious_sessions', methods=['GET'])
def get_user_suspicious_sessions(user_id):
    """View suspicious sessions for a specific user."""
    dataset = LogSessionDataset(session_length=5)
    user_sessions = []

    for x, y, uid, logs in DataLoader(dataset, batch_size=1, shuffle=False):
    # Flatten uid
        if isinstance(uid, (list, tuple)):
            uid = uid[0]
        if isinstance(uid, torch.Tensor):
            uid = uid.item()

        print(f"Comparing uid: {uid}  with requested user_id: {user_id}")

        if uid != user_id:
            continue

        x = x.to(DEVICE)
        score = transformer_model(x).item()
        # pred_label = int(score > 0.5)
        pred_label = int(score > 0.5)  # instead of 0.5

        if pred_label == 1:
            cleaned_logs = []
            for log in logs:
                clean_log = {}
                for key, value in log.items():
                    if isinstance(value, list) and len(value) == 1:
                        value = value[0]
                    if isinstance(value, torch.Tensor):
                        value = value.item()
                    clean_log[key] = value
                cleaned_logs.append(clean_log)

            user_sessions.append({
                "anomaly_score": round(score, 4),
                "logs": cleaned_logs
            })

    return jsonify(user_sessions)
