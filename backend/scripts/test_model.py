
#!/usr/bin/env python3

import joblib
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score
import matplotlib.pyplot as plt
import sqlite3

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
    threshold = np.percentile(scores, 10.0)  # Top 10% most anomalous
    preds = (scores < threshold).astype(int)

    plt.hist(scores, bins=50, alpha=0.7)
    plt.axvline(np.percentile(scores, 10), color='red', linestyle='--', label='10% threshold')
    plt.xlabel("Anomaly Score")
    plt.ylabel("Frequency")
    plt.title("IsolationForest Decision Function Scores")
    plt.legend()
    plt.show()

    print("Precision:", precision_score(y, preds))
    print("Recall:", recall_score(y, preds))
    print("F1 Score:", f1_score(y, preds))
    print("ROC AUC:", roc_auc_score(y, preds))

if __name__ == '__main__':
    test_model()
