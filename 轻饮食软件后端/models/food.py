import json
from models import db


class Food(db.Model):
    __tablename__ = 'foods'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, default='')
    image = db.Column(db.String(500), default='')
    calories = db.Column(db.Integer, default=0)
    protein = db.Column(db.Float, default=0)
    carbs = db.Column(db.Float, default=0)
    fat = db.Column(db.Float, default=0)
    fiber = db.Column(db.Float, default=0)
    tags = db.Column(db.String(200), default='')  # 逗号分隔
    ingredients = db.Column(db.Text, default='[]')  # JSON
    steps = db.Column(db.Text, default='[]')  # JSON
    benefits = db.Column(db.Text, default='')
    prep_time = db.Column(db.String(20), default='')
    difficulty = db.Column(db.String(20), default='简单')
    meal_type = db.Column(db.String(20), default='')  # breakfast/lunch/dinner/snack

    def to_dict(self):
        try:
            ingredients = json.loads(self.ingredients) if self.ingredients else []
        except (json.JSONDecodeError, TypeError):
            ingredients = []

        try:
            steps = json.loads(self.steps) if self.steps else []
        except (json.JSONDecodeError, TypeError):
            steps = []

        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'image': self.image,
            'calories': self.calories,
            'protein': self.protein,
            'carbs': self.carbs,
            'fat': self.fat,
            'fiber': self.fiber,
            'tags': [t.strip() for t in (self.tags or '').split(',') if t.strip()],
            'ingredients': ingredients,
            'steps': steps,
            'benefits': self.benefits,
            'prepTime': self.prep_time,
            'difficulty': self.difficulty,
            'mealType': self.meal_type,
        }

    def __repr__(self):
        return f'<Food {self.name}>'
