from backend.app import db

class UserLog(db.Model):
    __tablename__ = 'user_logs'
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.String(10), nullable=False)
    action_type = db.Column(db.String(50), nullable=False)
    resource = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(10), nullable=False)
    device = db.Column(db.String(20), nullable=False)
    hour_of_day = db.Column(db.Integer, nullable=False)
    num_files_accessed = db.Column(db.Integer, nullable=False)
    is_synthetic_anomaly = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'user_id': self.user_id,
            'action_type': self.action_type,
            'resource': self.resource,
            'location': self.location,
            'device': self.device,
            'hour_of_day': self.hour_of_day,
            'num_files_accessed': self.num_files_accessed
        }
