
#!/usr/bin/env python3
import os
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
import joblib
from sqlalchemy import create_engine
from dotenv import load_dotenv
import sqlite3

# Load environment variables
dotenv_path = Path(__file__).parents[3] / '.env'
load_dotenv(dotenv_path=dotenv_path)

def train_model():
    try:
        project_root = Path(__file__).parents[3]
        db_file = project_root / 'data' / 'user_logs.db'
        print(f"Loading data from: {db_file}")
        conn = sqlite3.connect(db_file)
        df = pd.read_sql_query("SELECT * FROM user_logs", conn)
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])

        # Feature engineering
        df['hour_sin'] = np.sin(2 * np.pi * df['hour_of_day'] / 24)
        df['hour_cos'] = np.cos(2 * np.pi * df['hour_of_day'] / 24)
        df['dow'] = df['timestamp'].dt.weekday
        df['dow_sin'] = np.sin(2 * np.pi * df['dow'] / 7)
        df['dow_cos'] = np.cos(2 * np.pi * df['dow'] / 7)

        # New behavioral features
        df['user_action_count'] = df.groupby('user_id')['timestamp'].transform('count')
        df['unique_resources'] = df.groupby('user_id')['resource'].transform('nunique')
        df['location_switches'] = df.groupby('user_id')['location'].transform(lambda x: (x != x.shift()).sum())
        df['avg_files_accessed'] = df.groupby('user_id')['num_files_accessed'].transform('mean')
        df['action_entropy'] = df.groupby('user_id')['action_type'].transform(lambda x: -np.sum(pd.Series(x).value_counts(normalize=True) * np.log2(pd.Series(x).value_counts(normalize=True) + 1e-9)))

        features = ['hour_sin', 'hour_cos', 'dow_sin', 'dow_cos',
                    'action_type', 'resource', 'location', 'device',
                    'num_files_accessed', 'user_action_count',
                    'unique_resources', 'location_switches',
                    'avg_files_accessed', 'action_entropy']

        df = df[features + ['is_synthetic_anomaly']].dropna()

        # Train only on normal data
        df_normal = df[df['is_synthetic_anomaly'] == 0]
        X = df_normal[features]

        cat_cols = X.select_dtypes(include=['object', 'category']).columns.tolist()
        num_cols = X.select_dtypes(include=['number']).columns.tolist()

        transformer = ColumnTransformer([
            ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), cat_cols),
            ('num', StandardScaler(), num_cols)
        ])

        pipe = Pipeline([
            ('transform', transformer),
            ('clf', IsolationForest(contamination=0.005, random_state=42))
        ])
        pipe.fit(X)

        joblib.dump(pipe, project_root / 'backend' / 'app' / 'models' / 'anomaly_model.pkl')
        print("✅ Model trained on normal data with engineered features.")

    except Exception as e:
        print(f"❌ Training failed: {e}")

if __name__ == '__main__':
    train_model()
