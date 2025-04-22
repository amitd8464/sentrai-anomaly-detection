
#!/usr/bin/env python3

from backend.app import create_app, db
from backend.app.models.log import UserLog
import random
from datetime import datetime, timedelta

def generate_logs(num_users: int = 10,
                  records_per_user: int = 500,
                  anomaly_ratio: float = 0.01):
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

        # 2) Anomalies: fully synthetic rogue logs
        total_normal_logs = num_users * records_per_user
        n_anomalies = int(total_normal_logs * anomaly_ratio)

        for _ in range(n_anomalies):
            ts = start_time + timedelta(seconds=random.randint(0, 30 * 24 * 3600))
            hour = random.choice([0, 1, 2, 3])  # unusual time
            ts = ts.replace(hour=hour)
            user = f'anon_user_{random.randint(900, 999)}'
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
        print(f"Generated {total_normal_logs} normal logs and {n_anomalies} synthetic anomalies.")

if __name__ == '__main__':
    generate_logs()
