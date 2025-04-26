#!/usr/bin/env python3

from backend.app import create_app, db
from backend.app.models.log import UserLog
import random
from datetime import datetime, timedelta

def generate_logs(num_users: int = 75,
                  records_per_user: int = 1000,
                  anomaly_session_users: int = 100,  # NEW: number of synthetic anomaly users
                  session_length: int = 5):           # NEW: session size
    """
    Generates synthetic user behavior logs in the SQLite database.
    """
    app = create_app()
    with app.app_context():
        db.drop_all()
        db.create_all()

        users = [f'U{str(i).zfill(3)}' for i in range(1, num_users + 1)]
        start_time = datetime.now() - timedelta(days=30)

        # 1) Normal logs
        for user in users:
            for _ in range(records_per_user):
                ts = start_time + timedelta(seconds=random.randint(0, 30 * 24 * 3600))
                action = random.choice(['login', 'download_file', 'access_resource'])
                resource = f'resource_{random.randint(1, 50)}'
                hour = ts.hour
                num_files = random.randint(1, 5) if action == 'download_file' else 0

                log = UserLog(
                    timestamp=ts,
                    user_id=user,
                    action_type=action,
                    resource=resource,
                    location=random.choice(['US', 'IN', 'UK']),
                    device=random.choice(['laptop', 'mobile', 'vpn']),
                    hour_of_day=hour,
                    num_files_accessed=num_files,
                    is_synthetic_anomaly=False
                )
                db.session.add(log)

        db.session.commit()

        # 2) Anomalous rogue sessions (FULL sessions with 5 logs per user)
        for i in range(anomaly_session_users):
            user = f'anon_user_{900 + i}'
            for _ in range(session_length):
                ts = start_time + timedelta(seconds=random.randint(0, 30 * 24 * 3600))
                hour = random.choice([0, 1, 2, 3])  # unusual times
                ts = ts.replace(hour=hour)
                resource = f'resource_{random.randint(999, 1000)}'
                action = random.choice(['scripted_exfil', 'unauthorized_access', 'debug_mode'])
                location = random.choice(['RU', 'CN', 'ZZ'])
                device = random.choice(['unknown_device', 'vpn'])
                num_files = random.randint(50, 100)

                log = UserLog(
                    timestamp=ts,
                    user_id=user,
                    action_type=action,
                    resource=resource,
                    location=location,
                    device=device,
                    hour_of_day=ts.hour,
                    num_files_accessed=num_files,
                    is_synthetic_anomaly=True
                )
                db.session.add(log)

        db.session.commit()
        total_normal_logs = num_users * records_per_user
        total_anomaly_logs = anomaly_session_users * session_length

        print(f"Generated {total_normal_logs} normal logs and {total_anomaly_logs} synthetic anomaly logs.")

if __name__ == '__main__':
    generate_logs()
