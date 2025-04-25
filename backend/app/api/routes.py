from flask import Blueprint, request, jsonify
import pandas as pd
import numpy as np
import joblib
from backend.app.models.log import UserLog
from backend.app.utils.detection import detect_anomalies
from pathlib import Path
import logging
from datetime import datetime
import random

api_bp = Blueprint('api', __name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

MODEL_PATH = Path(__file__).resolve().parent.parent / \
    'models' / 'anomaly_model.pkl'

try:
    pipeline = joblib.load(MODEL_PATH)
    logger.info(f"Successfully loaded model from {MODEL_PATH}")
except Exception as e:
    logger.error(f"Failed to load model: {e}")
    pipeline = None


@api_bp.route('/detect-anomaly', methods=['POST'])
def detect_anomaly():
    """
    Endpoint to detect if a log entry is anomalous.
    Expected JSON input:
    {
        "timestamp": "2025-04-20T14:30:00",
        "user_id": "user123",
        "action_type": "file_access",
        "resource": "financial_report",
        "location": "US",
        "device": "laptop",
        "hour_of_day": 14,
        "num_files_accessed": 5
    }
    Returns:
    {
        "is_anomaly": true/false,
        "anomaly_score": -0.123,
        "details": {
            "threshold": 0.05,
            "processed_at": "2025-04-20T15:00:00"
        }
    }
    """
    if pipeline is None:
        return jsonify({"error": "Model not loaded"}), 500
    try:
        # Get the JSON data
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Convert to DataFrame for processing
        log_df = pd.DataFrame([data])

        # Handle timestamp
        if 'timestamp' in log_df.columns:
            log_df['timestamp'] = pd.to_datetime(log_df['timestamp'])

        # Extract day of week if not provided
        if 'dow' not in log_df.columns and 'timestamp' in log_df.columns:
            log_df['dow'] = log_df['timestamp'].dt.weekday

        # Calculate cyclical features
        if 'hour_of_day' in log_df.columns:
            log_df['hour_sin'] = np.sin(2 * np.pi * log_df.hour_of_day / 24)
            log_df['hour_cos'] = np.cos(2 * np.pi * log_df.hour_of_day / 24)

        if 'dow' in log_df.columns:
            log_df['dow_sin'] = np.sin(2 * np.pi * log_df.dow / 7)
            log_df['dow_cos'] = np.cos(2 * np.pi * log_df.dow / 7)

        # ----------------------------------------------------------------
        # Handle categorical features - Apply One-Hot Encoding
        # ----------------------------------------------------------------
        categorical_columns = ['action_type', 'resource', 'location', 'device']
        encoded_df = pd.DataFrame()

        # Keep numeric columns as is
        numeric_columns = [
            col for col in log_df.columns if col not in categorical_columns + ['timestamp', 'user_id']]
        for col in numeric_columns:
            encoded_df[col] = log_df[col]

        # One-hot encode categorical columns
        for col in categorical_columns:
            if col in log_df.columns:
                # Get unique values for this column from your training data
                # This should match what was used during training
                if col == 'action_type':
                    # Example values - replace with your actual training values
                    known_values = [
                        'login', 'download_file', 'access_resource']
                elif col == 'resource':
                    known_values = [f'resource_{random.randint(1, 50)}']
                elif col == 'location':
                    known_values = ['US', 'IN', 'UK']
                elif col == 'device':
                    known_values = ['laptop', 'mobile', 'vpn']
                else:
                    # Default handling if column not specifically defined
                    known_values = []

                # Create columns for each known value
                for value in known_values:
                    col_name = f"{col}_{value}"
                    encoded_df[col_name] = (log_df[col] == value).astype(int)

        # Use the encoded DataFrame for prediction
        log_df = encoded_df

        # Required fields for the model - update to match encoded field names
        # Note: This needs to be updated based on your actual trained model's expected features
        # The one-hot encoded column names should match what was used during training

        # Convert all column names to strings to match the trained model
        log_df.columns = log_df.columns.astype(str)

        # Remove any unexpected columns
        # This might need adjustment based on your model's expected features
        expected_columns = [
            'num_files_accessed', 'hour_sin', 'hour_cos', 'dow_sin', 'dow_cos',
            'action_type_file_access', 'action_type_login', 'action_type_download_file',
            'action_type_modify_file', 'action_type_delete_file',
            'resource_financial_report', 'resource_customer_data', 'resource_hr_records',
            'resource_source_code', 'resource_admin_panel',
            'location_US', 'location_EU', 'location_APAC', 'location_remote',
            'device_laptop', 'device_desktop', 'device_mobile', 'device_tablet'
        ]

        # Keep only columns expected by the model
        # If your pipeline handles this correctly, you can comment out this part
        existing_columns = [
            col for col in expected_columns if col in log_df.columns]
        log_df = log_df[existing_columns]

        # Predict anomaly score
        anomaly_score = float(pipeline.decision_function(log_df)[0])

        # Convert to a 0-1 range where higher means more anomalous
        normalized_score = 1 - (anomaly_score + 0.5) / 0.5

        # Apply threshold (0.05 as per requirements)
        threshold = 0.05
        is_anomaly = normalized_score >= threshold

        # Prepare response
        response = {
            "is_anomaly": bool(is_anomaly),
            "anomaly_score": float(normalized_score),
            "details": {
                "threshold": threshold,
                "processed_at": datetime.now().isoformat()
            }
        }

        # Log the prediction
        logger.info(
            f"Anomaly detection request - Score: {normalized_score:.4f}, Is Anomaly: {is_anomaly}")
        return jsonify(response)
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return jsonify({"error": str(e)}), 500


@api_bp.route('/health', methods=['GET'])
def health():
    health_report = {}

    # DB check
    from backend.app import db
    from sqlalchemy import text
    try:
        db.session.execute(text('SELECT 1'))
        health_report['database'] = 'ok'
    except Exception as e:
        health_report['database'] = f'error: {e}'

    # Model check
    from backend.app.utils.detection import load_model
    try:
        load_model()
        health_report['model'] = 'ok'
    except Exception as e:
        health_report['model'] = f'error: {e}'

    status = 'healthy' if all(
        v == 'ok' for v in health_report.values()) else 'unhealthy'
    code = 200 if status == 'healthy' else 500
    return jsonify(status=status, details=health_report), code


@api_bp.route('/logs', methods=['GET'])
def get_logs():
    logs = UserLog.query.all()
    return jsonify([log.to_dict() for log in logs])


@api_bp.route('/detect-anomalies', methods=['POST'])
def detect():
    data = request.get_json()
    df = pd.DataFrame(data)

    results = detect_anomalies(df)
    return results

# --- SVM Anomalous Logs Endpoint ---
@app.route('/api/anomalous-logs')
def get_anomalous_logs():
    import pandas as pd
    from flask import jsonify
    file_path = Path(__file__).parents[2] / 'flagged_logs.csv'
    if not file_path.exists():
        return jsonify({"error": "flagged_logs.csv not found"}), 404
    df = pd.read_csv(file_path)
    return jsonify(df.to_dict(orient="records"))

# --- Transformer Suspicious Sessions Endpoint ---
@app.route('/api/suspicious-users')
def get_suspicious_sessions():
    import json
    from flask import jsonify
    file_path = Path(__file__).parents[2] / 'suspicious_sessions.json'
    if not file_path.exists():
        return jsonify({"error": "suspicious_sessions.json not found"}), 404
    with open(file_path) as f:
        data = json.load(f)
    return jsonify(data)
