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
    - num_users: number of distinct users to simulate
    - records_per_user: number of log entries per user
    - anomaly_ratio: fraction of total records to inject as anomalies
    """
    # Initialize Flask app & reset DB
    app = create_app()
    with app.app_context():
        db.drop_all()
        db.create_all()

        # 1) Generate normal user activity
        users = [f'U{str(i).zfill(3)}' for i in range(1, num_users + 1)]
        start_time = datetime.now() - timedelta(days=30)

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

        db.session.commit()  # commit normal logs

        # 2) Inject anomalies
        all_logs = UserLog.query.all()
        n_anoms = int(len(all_logs) * anomaly_ratio)

        for _ in range(n_anoms):
            log = random.choice(all_logs)
            log.is_synthetic_anomaly = True

            # a) pick an out-of-ordinary time
            h = random.choice([0, 1, 2, 3])
            log.timestamp = log.timestamp.replace(hour=h)
            log.hour_of_day = h

            # b) pick a never‑seen resource ID
            log.resource = f'resource_{random.randint(999, 1000)}'

            # c) other anomaly types
            anom_type = random.choice(['file_spike', 'odd_location', 'new_device'])

            if anom_type == 'file_spike':
                log.num_files_accessed = random.randint(50, 100)
            elif anom_type == 'odd_location':
                log.location = random.choice(['RU', 'CN', 'ZZ'])
            elif anom_type == 'new_device':
                log.device   = random.choice(['unknown_device', 'vpn'])

        db.session.commit()  # commit anomalies

        print(f"Generated {num_users * records_per_user} logs "
              f"with {n_anoms} injected anomalies.")

if __name__ == '__main__':
    generate_logs()
