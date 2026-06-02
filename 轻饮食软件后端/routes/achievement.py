from flask import Blueprint, jsonify, request, session
from models import db
from models.user import User
from models.food import Food
from models.achievement import Achievement, UserAchievement, AIBodyData

achievement_bp = Blueprint('achievement', __name__)


def get_current_user():
    user_id = session.get('user_id')
    if not user_id:
        return None
    return User.query.get(user_id)


@achievement_bp.route('/all', methods=['GET'])
def get_all():
    user = get_current_user()
    achievements = Achievement.query.all()

    unlocked_ids = set()
    if user:
        unlocked_ids = {ua.achievement_id for ua in UserAchievement.query.filter_by(user_id=user.id).all()}

    return jsonify([a.to_dict(unlocked=(a.id in unlocked_ids)) for a in achievements])


@achievement_bp.route('/unlocked', methods=['GET'])
def get_unlocked():
    user = get_current_user()
    if not user:
        return jsonify([])

    ua_list = UserAchievement.query.filter_by(user_id=user.id).all()
    result = []
    for ua in ua_list:
        achievement = Achievement.query.get(ua.achievement_id)
        if achievement:
            result.append(achievement.to_dict(unlocked=True))
    return jsonify(result)


@achievement_bp.route('/ai/body-data', methods=['POST'])
def submit_body_data():
    user = get_current_user()
    if not user:
        return jsonify({'success': False, 'message': '未登录'}), 401

    data = request.get_json()
    height = data.get('height', 0)
    weight = data.get('weight', 0)
    bmi = round(weight / ((height / 100) ** 2), 1) if height > 0 else 0

    body_data = AIBodyData(
        user_id=user.id,
        gender=data.get('gender', ''),
        age=data.get('age', 0),
        height=height,
        weight=weight,
        body_fat=data.get('body_fat', 0),
        bmi=bmi,
        daily_calories=data.get('dailyCalories', 1500),
        protein=data.get('protein', 95),
        carbs=data.get('carbs', 140),
        fat=data.get('fat', 45)
    )
    db.session.add(body_data)

    user.gender = data.get('gender', user.gender)
    user.age = data.get('age', user.age)
    user.height = height or user.height
    user.weight = weight or user.weight
    user.body_fat = data.get('body_fat', user.body_fat)

    db.session.commit()
    return jsonify({'success': True})


@achievement_bp.route('/ai/plan', methods=['GET'])
def get_plan():
    user = get_current_user()
    if not user:
        return jsonify({'success': False, 'message': '未登录'}), 401

    body_data = AIBodyData.query.filter_by(user_id=user.id).order_by(AIBodyData.created_at.desc()).first()

    # 计算BMI和每日热量
    height = body_data.height if body_data else user.height
    weight = body_data.weight if body_data else user.weight
    bmi = round(weight / ((height / 100) ** 2), 1) if height > 0 else 22.5

    # 基于BMR计算每日热量需求 (Harris-Benedict公式)
    age = body_data.age if body_data else user.age or 25
    gender = body_data.gender if body_data else user.gender or 'male'

    if gender == 'male':
        bmr = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
    else:
        bmr = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)

    # 根据目标调整热量
    daily_calories = int(bmr * 0.85)  # 减脂：减少15%
    if daily_calories < 1200:
        daily_calories = 1200

    # 计算宏量营养素
    protein = int(weight * 1.5)  # 每公斤体重1.5g蛋白质
    fat = int(daily_calories * 0.25 / 9)  # 25%热量来自脂肪
    carbs = int((daily_calories - protein * 4 - fat * 9) / 4)  # 剩余来自碳水

    # 从食物库获取食物推荐
    foods = Food.query.all()

    # 按餐次分类食物
    breakfast_foods = [f for f in foods if f.meal_type == 'breakfast'] or foods[:10]
    lunch_foods = [f for f in foods if f.meal_type == 'lunch'] or foods[10:20]
    dinner_foods = [f for f in foods if f.meal_type == 'dinner'] or foods[20:30]
    snack_foods = [f for f in foods if f.meal_type == 'snack'] or foods[30:40]

    # 为每个餐次选择2-3个推荐
    import random
    def select_meals(food_list, count=2):
        if len(food_list) <= count:
            selected = food_list
        else:
            selected = random.sample(food_list, count)
        return [{
            'id': f.id,
            'name': f.name,
            'calories': f.calories,
            'protein': f.protein,
            'carbs': f.carbs,
            'fat': f.fat,
            'tags': [t.strip() for t in f.tags.split(',') if t.strip()] if f.tags else [],
            'image': f.image
        } for f in selected]

    return jsonify({
        'bmi': bmi,
        'dailyCalories': daily_calories,
        'macros': {
            'protein': protein,
            'carbs': carbs,
            'fat': fat
        },
        'meals': {
            'breakfast': select_meals(breakfast_foods),
            'lunch': select_meals(lunch_foods),
            'snack': select_meals(snack_foods, 1),
            'dinner': select_meals(dinner_foods)
        }
    })


@achievement_bp.route('/ai/apply', methods=['POST'])
def apply_plan():
    user = get_current_user()
    if not user:
        return jsonify({'success': False, 'message': '未登录'}), 401

    user.plan_days = user.plan_days + 1
    db.session.commit()
    return jsonify({'success': True})
