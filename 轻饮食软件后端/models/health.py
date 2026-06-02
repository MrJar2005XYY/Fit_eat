from datetime import datetime
from models import db


class HealthRecord(db.Model):
    """健康记录表"""
    __tablename__ = 'health_records'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    record_type = db.Column(db.String(20), nullable=False)  # weight/body_fat/blood_sugar/blood_pressure
    value = db.Column(db.Float, default=0)
    value2 = db.Column(db.Float, default=0)  # 用于血压的舒张压
    unit = db.Column(db.String(10), default='')
    notes = db.Column(db.Text, default='')
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def to_dict(self):
        return {
            'id': self.id,
            'type': self.record_type,
            'value': self.value,
            'value2': self.value2,
            'unit': self.unit,
            'notes': self.notes,
            'time': self.recorded_at.strftime('%Y-%m-%d %H:%M') if self.recorded_at else '',
            'date': self.recorded_at.strftime('%Y-%m-%d') if self.recorded_at else '',
        }

    def __repr__(self):
        return f'<HealthRecord {self.record_type} {self.value}>'
