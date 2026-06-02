from datetime import datetime
from models import db


class ExerciseType(db.Model):
    """运动类型表"""
    __tablename__ = 'exercise_types'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    category = db.Column(db.String(20), default='')  # cardio/strength/flexibility/sports
    met = db.Column(db.Float, default=5.0)  # MET值（代谢当量）
    icon = db.Column(db.String(50), default='fitness_center')
    description = db.Column(db.String(200), default='')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'met': self.met,
            'icon': self.icon,
            'description': self.description,
        }

    def __repr__(self):
        return f'<ExerciseType {self.name}>'


class ExerciseRecord(db.Model):
    """运动记录表"""
    __tablename__ = 'exercise_records'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    exercise_type_id = db.Column(db.Integer, db.ForeignKey('exercise_types.id'), nullable=True)
    exercise_name = db.Column(db.String(50), default='')
    duration = db.Column(db.Integer, default=0)  # 分钟
    calories = db.Column(db.Integer, default=0)  # 消耗的卡路里
    distance = db.Column(db.Float, default=0)  # 距离（公里），用于跑步/骑行等
    heart_rate = db.Column(db.Integer, default=0)  # 平均心率
    notes = db.Column(db.Text, default='')
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    exercise_type = db.relationship('ExerciseType', backref='records')

    def to_dict(self):
        return {
            'id': self.id,
            'exerciseTypeId': self.exercise_type_id,
            'name': self.exercise_name or (self.exercise_type.name if self.exercise_type else ''),
            'category': self.exercise_type.category if self.exercise_type else '',
            'icon': self.exercise_type.icon if self.exercise_type else 'fitness_center',
            'duration': self.duration,
            'calories': self.calories,
            'distance': self.distance,
            'heartRate': self.heart_rate,
            'notes': self.notes,
            'time': self.recorded_at.strftime('%Y-%m-%d %H:%M') if self.recorded_at else '',
            'met': self.exercise_type.met if self.exercise_type else 5.0,
        }

    def __repr__(self):
        return f'<ExerciseRecord {self.exercise_name} {self.recorded_at}>'
