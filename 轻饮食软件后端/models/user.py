from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from models import db


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.String(64), unique=True, nullable=False, index=True)
    username = db.Column(db.String(64), nullable=False, default='')
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    avatar = db.Column(db.String(500), default='')
    bio = db.Column(db.String(200), default='')

    # 身体数据
    gender = db.Column(db.String(10), default='')
    age = db.Column(db.Integer, default=0)
    height = db.Column(db.Float, default=0)
    weight = db.Column(db.Float, default=0)
    body_fat = db.Column(db.Float, default=0)
    target_calories = db.Column(db.Integer, default=1800)
    target_weight = db.Column(db.Float, default=0)

    # 统计
    plan_days = db.Column(db.Integer, default=0)

    # 运动目标
    weekly_exercise_goal = db.Column(db.Integer, default=3)  # 每周运动次数目标
    daily_exercise_duration = db.Column(db.Integer, default=30)  # 每日运动时长目标(分钟)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 关系
    diet_records = db.relationship('DietRecord', backref='user', lazy='dynamic')
    water_records = db.relationship('WaterRecord', backref='user', lazy='dynamic')
    posts = db.relationship('CommunityPost', backref='user', lazy='dynamic')
    achievements = db.relationship('UserAchievement', backref='user', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'accountId': self.account_id,
            'name': self.username,
            'avatar': self.avatar,
            'bio': self.bio,
            'gender': self.gender,
            'age': self.age,
            'height': self.height,
            'weight': self.weight,
            'body_fat': self.body_fat,
            'bmi': round(self.weight / ((self.height / 100) ** 2), 1) if self.height > 0 else 0,
            'targetWeight': self.target_weight,
            'targetCalories': self.target_calories,
            'currentWeight': self.weight,
            'planDays': self.plan_days,
            'weeklyExerciseGoal': self.weekly_exercise_goal,
            'dailyExerciseDuration': self.daily_exercise_duration,
            'recordCount': self.diet_records.count(),
            'achievementCount': self.achievements.count(),
        }

    def __repr__(self):
        return f'<User {self.username}>'
