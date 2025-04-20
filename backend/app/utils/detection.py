
import os
import joblib
import pandas as pd
import numpy as np
from pathlib import Path
from flask import jsonify

model_path = Path(__file__).parents[1] / 'models' / 'anomaly_model.pkl'
_model = None

def load_model():
    global _model
    if _model is None:
        _model = joblib.load(model_path)
    return _model

def detect_anomalies(df: pd.DataFrame) -> list:
    try:
        model = load_model()

        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['hour_sin'] = np.sin(2 * np.pi * df['hour_of_day'] / 24)
        df['hour_cos'] = np.cos(2 * np.pi * df['hour_of_day'] / 24)
        df['dow'] = df['timestamp'].dt.weekday
        df['dow_sin'] = np.sin(2 * np.pi * df['dow'] / 7)
        df['dow_cos'] = np.cos(2 * np.pi * df['dow'] / 7)

        # Feature engineering
        df['user_action_count'] = df.groupby('user_id')['timestamp'].transform('count')
        df['unique_resources'] = df.groupby('user_id')['resource'].transform('nunique')
        df['location_switches'] = df.groupby('user_id')['location'].transform(lambda x: (x != x.shift()).sum())
        df['avg_files_accessed'] = df.groupby('user_id')['num_files_accessed'].transform('mean')
        df['action_entropy'] = df.groupby('user_id')['action_type'].transform(
            lambda x: -np.sum(pd.Series(x).value_counts(normalize=True) * np.log2(pd.Series(x).value_counts(normalize=True) + 1e-9))
        )

        features = ['hour_sin', 'hour_cos', 'dow_sin', 'dow_cos',
                    'action_type', 'resource', 'location', 'device',
                    'num_files_accessed', 'user_action_count',
                    'unique_resources', 'location_switches',
                    'avg_files_accessed', 'action_entropy']

        df_clean = df[features].copy()
        X_transformed = model.named_steps['transform'].transform(df_clean)
        scores = model.named_steps['clf'].decision_function(X_transformed)
        threshold = np.percentile(scores, 1.0)
        preds = (scores < threshold).astype(int)

        return preds.tolist()
    except Exception as e:
        print(f"❌ Detection error: {e}")
        return []
