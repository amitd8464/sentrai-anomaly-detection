import os
from pathlib import Path
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from dotenv import load_dotenv
import pandas as pd
import torch
from backend.app.models.train_transformer_session_model import SessionTransformer, LogSessionDataset, DEVICE
from torch.utils.data import DataLoader
import joblib
import sqlite3

db = SQLAlchemy()

def create_app():
    dotenv_path = Path(__file__).parents[1].parent / 'backend' / '.env'
    load_dotenv(dotenv_path=dotenv_path)

    app = Flask(__name__, instance_relative_config=True)

    # Configs
    project_root = Path(__file__).parents[2]
    data_dir = project_root / 'data'
    data_dir.mkdir(parents=True, exist_ok=True)
    db_file = data_dir / 'user_logs.db'

    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev')
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_file}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    CORS(app)
    db.init_app(app)

    with app.app_context():
        from backend.app.api.routes import api_bp
        from backend.app.api.anomaly_routes import anomaly_bp
        from backend.app.models.log import UserLog

        db.create_all()
        app.register_blueprint(api_bp, url_prefix='/api')
        app.register_blueprint(anomaly_bp, url_prefix='/anomaly')

        # 🔥 Cache df_logs once
        app.df_logs = load_user_logs()

        # 🔥 Cache suspicious sessions once
        app.suspicious_sessions = load_suspicious_sessions()

    return app

# --- Helper functions ---
def load_user_logs():
    db_file = Path(__file__).parents[2] / 'data' / 'user_logs.db'
    conn = sqlite3.connect(db_file)
    df = pd.read_sql_query("SELECT * FROM user_logs ORDER BY timestamp", conn)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df

def load_suspicious_sessions():
    dataset = LogSessionDataset(session_length=5)
    transformer_model = SessionTransformer(input_dim=6)
    model_path = Path(__file__).parents[1] / "app" / "models" / "session_transformer.pt"
    transformer_model.load_state_dict(torch.load(model_path, map_location=DEVICE))
    transformer_model.to(DEVICE)
    transformer_model.eval()

    suspicious_sessions = []

    for x, y, user_id, logs in DataLoader(dataset, batch_size=1, shuffle=False):
        if isinstance(user_id, (list, tuple)):
            user_id = user_id[0]
        if isinstance(user_id, torch.Tensor):
            user_id = user_id.item()

        x = x.to(DEVICE)
        score = transformer_model(x).item()

        if score > 0.5:
            suspicious_sessions.append({
                "user_id": user_id,
                "anomaly_score": round(score, 4),
                "logs": [clean_log_entry(log) for log in logs]
            })

    return suspicious_sessions

def clean_log_entry(entry):
    clean_entry = {}
    for key, value in entry.items():
        if isinstance(value, list) and len(value) == 1:
            value = value[0]
        if isinstance(value, torch.Tensor):
            value = value.item()
        clean_entry[key] = value
    return clean_entry
