from datetime import datetime
from models import db


class DietRecord(db.Model):
    __tablename__ = 'diet_records'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    food_id = db.Column(db.Integer, db.ForeignKey('foods.id'), nullable=True)
    food_name = db.Column(db.String(100), default='')
    meal_type = db.Column(db.String(20), default='')  # breakfast/lunch/dinner/snack
    calories = db.Column(db.Integer, default=0)
    protein = db.Column(db.Float, default=0)
    carbs = db.Column(db.Float, default=0)
    fat = db.Column(db.Float, default=0)
    fiber = db.Column(db.Float, default=0)
    image = db.Column(db.String(500), default='')
    description = db.Column(db.String(200), default='')
    amount = db.Column(db.Float, default=1.0)
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    food = db.relationship('Food', backref='diet_records')

    def to_dict(self):
        return {
            'id': self.id,
            'foodId': self.food_id,
            'name': self.food_name or (self.food.name if self.food else ''),
            'meal': self.meal_type,
            'calories': self.calories,
            'protein': self.protein,
            'carbs': self.carbs,
            'fat': self.fat,
            'fiber': self.fiber,
            'image': self.image or (self.food.image if self.food else ''),
            'description': self.description,
            'amount': self.amount,
            'time': self.recorded_at.strftime('%Y-%m-%d %H:%M'),
        }

    def __repr__(self):
        return f'<DietRecord {self.food_name} {self.recorded_at}>'


class WaterRecord(db.Model):
    __tablename__ = 'water_records'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    amount = db.Column(db.Integer, default=250)  # ml
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<WaterRecord {self.amount}ml {self.recorded_at}>'
