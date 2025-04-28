# backend/app/api/anomaly_routes.py

from flask import Blueprint, jsonify, request, current_app
import numpy as np
import pandas as pd

anomaly_bp = Blueprint('anomaly_bp', __name__)

@anomaly_bp.route('/logs', methods=['GET'])
def get_all_logs():
    """View all user logs."""
    df = current_app.df_logs
    logs = df.to_dict(orient='records')
    return jsonify(logs)

@anomaly_bp.route('/logs/flagged', methods=['GET'])
def get_flagged_logs():
    """View logs flagged by OneClassSVM model."""
    df = current_app.df_logs.copy()

    # Compute cyclical features
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['day_of_week'] = df['timestamp'].dt.dayofweek
    df['hour_cos'] = np.cos(2 * np.pi * df['hour_of_day'] / 24)
    df['hour_sin'] = np.sin(2 * np.pi * df['hour_of_day'] / 24)
    df['dow_cos'] = np.cos(2 * np.pi * df['day_of_week'] / 7)
    df['dow_sin'] = np.sin(2 * np.pi * df['day_of_week'] / 7)

    feature_cols = ['hour_cos', 'hour_sin', 'dow_cos', 'dow_sin', 
                    'hour_of_day', 'num_files_accessed', 'action_type', 'resource', 'location', 'device']

    features = df[feature_cols]

    # Reload model (cached later for production)
    from backend.app import joblib
    from pathlib import Path
    ocsvm_model = joblib.load(Path(__file__).parents[2] / 'app' / 'models' / 'anomaly_pipeline.pkl')

    preds = ocsvm_model.predict(features)

    flagged_logs = df[preds == -1].to_dict(orient='records')
    return jsonify(flagged_logs)

@anomaly_bp.route('/users/suspicious', methods=['GET'])
def get_suspicious_users():
    """View suspicious users based on Transformer model."""
    sessions = current_app.suspicious_sessions
    suspicious_users = list(set(session['user_id'] for session in sessions))
    return jsonify(suspicious_users)

@anomaly_bp.route('/users/<string:user_id>/suspicious_sessions', methods=['GET'])
def get_user_suspicious_sessions(user_id):
    """View suspicious sessions for a specific user."""
    sessions = current_app.suspicious_sessions
    user_sessions = [session for session in sessions if session['user_id'] == user_id]
    return jsonify(user_sessions)

@anomaly_bp.route('/refresh', methods=['POST'])
def refresh_anomaly_data():
    """Refresh user logs and suspicious sessions."""
    from backend.app import load_user_logs, load_suspicious_sessions

    # Reload and cache fresh logs
    current_app.df_logs = load_user_logs()
    # Reload and cache fresh suspicious sessions
    current_app.suspicious_sessions = load_suspicious_sessions()

    return jsonify({"message": "✅ Refreshed logs and suspicious sessions successfully!"}), 200
