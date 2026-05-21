from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class MonitoringMetric(db.Model):
    __tablename__ = "monitoring_metrics"

    id = db.Column(db.Integer, primary_key=True)
    hostname = db.Column(db.String(100), nullable=False)
    cpu_usage = db.Column(db.Float, nullable=False)
    memory_usage = db.Column(db.Float, nullable=False)
    disk_usage = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "hostname": self.hostname,
            "cpu_usage": self.cpu_usage,
            "memory_usage": self.memory_usage,
            "disk_usage": self.disk_usage,
            "status": self.status,
            "timestamp": self.timestamp.isoformat()
        }
