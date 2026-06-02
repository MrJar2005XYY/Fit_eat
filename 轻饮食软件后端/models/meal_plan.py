from datetime import datetime
from models import db


class MealPlan(db.Model):
    """饮食计划表"""
    __tablename__ = 'meal_plans'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    name = db.Column(db.String(100), default='')
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    target_calories = db.Column(db.Integer, default=1800)
    notes = db.Column(db.Text, default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    items = db.relationship('MealPlanItem', backref='plan', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self, include_items=False):
        result = {
            'id': self.id,
            'name': self.name,
            'startDate': self.start_date.strftime('%Y-%m-%d') if self.start_date else '',
            'endDate': self.end_date.strftime('%Y-%m-%d') if self.end_date else '',
            'targetCalories': self.target_calories,
            'notes': self.notes,
            'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else '',
            'itemCount': self.items.count(),
        }
        if include_items:
            result['items'] = [item.to_dict() for item in self.items.all()]
        return result

    def __repr__(self):
        return f'<MealPlan {self.name}>'


class MealPlanItem(db.Model):
    """饮食计划项目表"""
    __tablename__ = 'meal_plan_items'

    id = db.Column(db.Integer, primary_key=True)
    plan_id = db.Column(db.Integer, db.ForeignKey('meal_plans.id'), nullable=False, index=True)
    food_id = db.Column(db.Integer, db.ForeignKey('foods.id'), nullable=True)
    food_name = db.Column(db.String(100), default='')
    meal_type = db.Column(db.String(20), default='')  # breakfast/lunch/dinner/snack
    day_of_week = db.Column(db.Integer, default=0)  # 0=周一, 6=周日
    calories = db.Column(db.Integer, default=0)
    protein = db.Column(db.Float, default=0)
    carbs = db.Column(db.Float, default=0)
    fat = db.Column(db.Float, default=0)
    amount = db.Column(db.Float, default=1.0)
    is_completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime, nullable=True)

    food = db.relationship('Food', backref='meal_plan_items')

    def to_dict(self):
        return {
            'id': self.id,
            'planId': self.plan_id,
            'foodId': self.food_id,
            'name': self.food_name or (self.food.name if self.food else ''),
            'mealType': self.meal_type,
            'dayOfWeek': self.day_of_week,
            'calories': self.calories,
            'protein': self.protein,
            'carbs': self.carbs,
            'fat': self.fat,
            'amount': self.amount,
            'isCompleted': self.is_completed,
            'completedAt': self.completed_at.strftime('%Y-%m-%d %H:%M') if self.completed_at else None,
            'image': self.food.image if self.food else '',
        }

    def __repr__(self):
        return f'<MealPlanItem {self.food_name}>'
