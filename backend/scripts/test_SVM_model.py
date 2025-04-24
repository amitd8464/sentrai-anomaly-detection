
#!/usr/bin/env python3

import joblib
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score, roc_curve
import sqlite3
import csv

def test_model():
    model_path = Path(__file__).parents[1] / 'app' / 'models' / 'anomaly_model.pkl'
    pipeline = joblib.load(model_path)

    db_file = Path(__file__).parents[2] / 'data' / 'user_logs.db'
    conn = sqlite3.connect(db_file)
    df = pd.read_sql_query("SELECT * FROM user_logs", conn)
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    df['hour_sin'] = np.sin(2 * np.pi * df['hour_of_day'] / 24)
    df['hour_cos'] = np.cos(2 * np.pi * df['hour_of_day'] / 24)
    df['dow'] = df['timestamp'].dt.weekday
    df['dow_sin'] = np.sin(2 * np.pi * df['dow'] / 7)
    df['dow_cos'] = np.cos(2 * np.pi * df['dow'] / 7)

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
    X = df[features]
    y = df['is_synthetic_anomaly']

    X_transformed = pipeline.named_steps['transform'].transform(X)
    scores = pipeline.named_steps['clf'].decision_function(X_transformed)

    # ROC-based threshold
    fpr, tpr, thresholds = roc_curve(y, scores)
    best_thresh = thresholds[np.argmax(tpr - fpr)]
    preds = (scores < best_thresh).astype(int)

    print(f"ROC-AUC Best Threshold: {best_thresh:.4f}")
    print("Precision:", precision_score(y, preds))
    print("Recall:", recall_score(y, preds))
    print("F1 Score:", f1_score(y, preds))
    print("ROC AUC:", roc_auc_score(y, preds))

    df['anomaly_score'] = scores
    df['predicted_anomaly'] = preds
    df['true_label'] = y
    df[preds == 1].to_csv("flagged_logs.csv", index=False)
    print("✅ Flagged logs saved to flagged_logs.csv")

if __name__ == '__main__':
    test_model()
