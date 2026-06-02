from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, session
from sqlalchemy import func
from models import db
from models.user import User
from models.food import Food
from models.diet import DietRecord, WaterRecord
from models.exercise import ExerciseRecord

diet_bp = Blueprint('diet', __name__)


def get_current_user():
    user_id = session.get('user_id')
    if not user_id:
        return None
    return User.query.get(user_id)


def today_range():
    now = datetime.utcnow()
    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=1)
    return start, end


@diet_bp.route('/today-calories', methods=['GET'])
def today_calories():
    user = get_current_user()
    if not user:
        return jsonify({'success': False, 'message': '未登录'}), 401

    start, end = today_range()

    # 计算饮食摄入
    consumed = db.session.query(func.coalesce(func.sum(DietRecord.calories), 0)).filter(
        DietRecord.user_id == user.id,
        DietRecord.recorded_at >= start,
        DietRecord.recorded_at < end
    ).scalar()

    # 计算运动消耗
    burned = db.session.query(func.coalesce(func.sum(ExerciseRecord.calories), 0)).filter(
        ExerciseRecord.user_id == user.id,
        ExerciseRecord.recorded_at >= start,
        ExerciseRecord.recorded_at < end
    ).scalar()

    target = user.target_calories or 1800
    remaining = max(target - int(consumed) + int(burned), 0)

    return jsonify({
        'target': target,
        'consumed': int(consumed),
        'burned': int(burned),
        'remaining': remaining
    })


@diet_bp.route('/today-meals', methods=['GET'])
def today_meals():
    user = get_current_user()
    if not user:
        return jsonify({'success': False, 'message': '未登录'}), 401

    start, end = today_range()
    records = DietRecord.query.filter(
        DietRecord.user_id == user.id,
        DietRecord.recorded_at >= start,
        DietRecord.recorded_at < end
    ).order_by(DietRecord.recorded_at.desc()).all()

    return jsonify([r.to_dict() for r in records])


@diet_bp.route('/records', methods=['GET'])
def get_records():
    user = get_current_user()
    if not user:
        return jsonify({'success': False, 'message': '未登录'}), 401

    date = request.args.get('date')
    query = DietRecord.query.filter_by(user_id=user.id)

    if date:
        try:
            d = datetime.strptime(date, '%Y-%m-%d')
            query = query.filter(
                DietRecord.recorded_at >= d,
                DietRecord.recorded_at < d + timedelta(days=1)
            )
        except ValueError:
            pass

    records = query.order_by(DietRecord.recorded_at.desc()).all()
    return jsonify([r.to_dict() for r in records])


@diet_bp.route('/records', methods=['POST'])
def add_record():
    user = get_current_user()
    if not user:
        return jsonify({'success': False, 'message': '未登录'}), 401

    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': '请求数据无效'}), 400
    amount = data.get('amount', 1.0)

    # 如果有food_id，从Food表获取营养数据
    calories = data.get('calories', 0)
    protein = data.get('protein', 0)
    carbs = data.get('carbs', 0)
    fat = data.get('fat', 0)
    fiber = data.get('fiber', 0)

    food_id = data.get('foodId')
    if food_id:
        food = Food.query.get(food_id)
        if food:
            calories = int(food.calories * amount)
            protein = round(food.protein * amount, 1)
            carbs = round(food.carbs * amount, 1)
            fat = round(food.fat * amount, 1)
            fiber = round(food.fiber * amount, 1)

    record = DietRecord(
        user_id=user.id,
        food_id=food_id,
        food_name=data.get('name', ''),
        meal_type=data.get('meal', ''),
        calories=calories,
        protein=protein,
        carbs=carbs,
        fat=fat,
        fiber=fiber,
        image=data.get('image', ''),
        description=data.get('description', ''),
        amount=amount
    )
    db.session.add(record)
    db.session.commit()

    # 检查成就解锁
    from routes.achievement import check_and_unlock_achievements
    check_and_unlock_achievements(user.id)

    return jsonify({'success': True, 'id': record.id})


@diet_bp.route('/records/<int:record_id>', methods=['DELETE'])
def delete_record(record_id):
    user = get_current_user()
    if not user:
        return jsonify({'success': False, 'message': '未登录'}), 401

    record = DietRecord.query.filter_by(id=record_id, user_id=user.id).first()
    if not record:
        return jsonify({'success': False, 'message': '记录不存在'}), 404

    db.session.delete(record)
    db.session.commit()
    return jsonify({'success': True})


@diet_bp.route('/macros', methods=['GET'])
def get_macros():
    user = get_current_user()
    if not user:
        return jsonify({'success': False, 'message': '未登录'}), 401

    start, end = today_range()
    records = DietRecord.query.filter(
        DietRecord.user_id == user.id,
        DietRecord.recorded_at >= start,
        DietRecord.recorded_at < end
    ).all()

    protein = sum(r.protein for r in records)
    carbs = sum(r.carbs for r in records)
    fat = sum(r.fat for r in records)
    return jsonify({
        'protein': {'current': round(protein), 'target': 80},
        'carbs': {'current': round(carbs), 'target': 200},
        'fat': {'current': round(fat), 'target': 60}
    })


@diet_bp.route('/water', methods=['GET'])
def get_water():
    user = get_current_user()
    if not user:
        return jsonify({'success': False, 'message': '未登录'}), 401

    start, end = today_range()
    total = db.session.query(func.coalesce(func.sum(WaterRecord.amount), 0)).filter(
        WaterRecord.user_id == user.id,
        WaterRecord.recorded_at >= start,
        WaterRecord.recorded_at < end
    ).scalar()

    current = int(total)
    return jsonify({
        'target': 2500,
        'current': current,
        'cups': 10,
        'filledCups': current // 250
    })


@diet_bp.route('/water', methods=['PUT'])
def update_water():
    user = get_current_user()
    if not user:
        return jsonify({'success': False, 'message': '未登录'}), 401

    data = request.get_json()
    amount = data.get('amount', 250)
    record = WaterRecord(user_id=user.id, amount=amount)
    db.session.add(record)
    db.session.commit()
    return jsonify({'success': True})


@diet_bp.route('/weekly-calories', methods=['GET'])
def weekly_calories():
    user = get_current_user()
    if not user:
        return jsonify({'success': False, 'message': '未登录'}), 401

    target = user.target_calories or 1800
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    weekday = today.weekday()
    week_start = today - timedelta(days=weekday)

    days = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
    result = []

    for i in range(7):
        day_start = week_start + timedelta(days=i)
        day_end = day_start + timedelta(days=1)
        consumed = db.session.query(func.coalesce(func.sum(DietRecord.calories), 0)).filter(
            DietRecord.user_id == user.id,
            DietRecord.recorded_at >= day_start,
            DietRecord.recorded_at < day_end
        ).scalar()
        result.append({
            'day': days[i],
            'consumed': int(consumed),
            'target': target
        })

    return jsonify(result)


@diet_bp.route('/nutrition-radar', methods=['GET'])
def nutrition_radar():
    user = get_current_user()
    if not user:
        return jsonify({'success': False, 'message': '未登录'}), 401

    start, end = today_range()
    records = DietRecord.query.filter(
        DietRecord.user_id == user.id,
        DietRecord.recorded_at >= start,
        DietRecord.recorded_at < end
    ).all()

    total_calories = sum(r.calories for r in records)
    total_protein = sum(r.protein for r in records)
    total_carbs = sum(r.carbs for r in records)
    total_fat = sum(r.fat for r in records)
    total_fiber = sum(r.fiber for r in records)

    target = user.target_calories or 1800

    # 基于推荐摄入量计算各维度百分比
    # 蛋白质推荐: 80g, 碳水推荐: 200g, 脂肪推荐: 60g, 纤维推荐: 25g
    # 维生素和矿物质基于食物多样性估算
    energy_pct = min(round(total_calories / target * 100), 100) if target else 0
    protein_pct = min(round(total_protein / 80 * 100), 100)
    fat_pct = min(round(total_fat / 60 * 100), 100)
    fiber_pct = min(round(total_fiber / 25 * 100), 100)

    # 维生素和矿物质基于食物种类数量估算
    food_types = len(set(r.food_id for r in records if r.food_id))
    vitamins_pct = min(food_types * 15, 100)  # 每种食物约15%贡献
    minerals_pct = min(food_types * 12, 100)  # 每种食物约12%贡献

    return jsonify({
        'energy': energy_pct,
        'protein': protein_pct,
        'fat': fat_pct,
        'fiber': fiber_pct,
        'vitamins': vitamins_pct,
        'minerals': minerals_pct
    })


@diet_bp.route('/suggest', methods=['GET'])
def suggest_meals():
    """智能餐食搭配推荐"""
    user = get_current_user()
    if not user:
        return jsonify({'success': False, 'message': '未登录'}), 401

    meal_type = request.args.get('meal', '')
    if not meal_type:
        # 根据当前时间判断餐次
        hour = datetime.utcnow().hour
        if hour < 10:
            meal_type = 'breakfast'
        elif hour < 14:
            meal_type = 'lunch'
        elif hour < 17:
            meal_type = 'snack'
        else:
            meal_type = 'dinner'

    # 获取今日已摄入的营养
    start, end = today_range()
    records = DietRecord.query.filter(
        DietRecord.user_id == user.id,
        DietRecord.recorded_at >= start,
        DietRecord.recorded_at < end
    ).all()

    consumed_calories = sum(r.calories for r in records)
    consumed_protein = sum(r.protein for r in records)
    consumed_carbs = sum(r.carbs for r in records)
    consumed_fat = sum(r.fat for r in records)

    target = user.target_calories or 1800
    remaining_calories = max(target - consumed_calories, 0)

    # 根据剩余营养需求推荐食物
    from models.food import Food

    # 计算该餐次建议热量占比
    meal_ratio = {'breakfast': 0.3, 'lunch': 0.35, 'snack': 0.1, 'dinner': 0.25}
    suggested_calories = int(remaining_calories * meal_ratio.get(meal_type, 0.3))

    # 推荐食物：热量在建议范围内的该餐次食物
    min_cal = max(suggested_calories - 200, 50)
    max_cal = suggested_calories + 200

    foods = Food.query.filter(
        Food.meal_type == meal_type,
        Food.calories.between(min_cal, max_cal)
    ).limit(6).all()

    # 如果该餐次食物不够，补充其他餐次的食物
    if len(foods) < 3:
        other_foods = Food.query.filter(
            Food.meal_type != meal_type,
            Food.calories.between(min_cal, max_cal)
        ).limit(3).all()
        foods.extend(other_foods)

    return jsonify({
        'mealType': meal_type,
        'suggestedCalories': suggested_calories,
        'remainingCalories': remaining_calories,
        'consumed': {
            'calories': consumed_calories,
            'protein': round(consumed_protein, 1),
            'carbs': round(consumed_carbs, 1),
            'fat': round(consumed_fat, 1),
        },
        'suggestions': [f.to_dict() for f in foods[:6]]
    })


@diet_bp.route('/monthly-report', methods=['GET'])
def monthly_report():
    """月度饮食报告"""
    user = get_current_user()
    if not user:
        return jsonify({'success': False, 'message': '未登录'}), 401

    today = datetime.utcnow()
    month = request.args.get('month', today.month, type=int)
    year = request.args.get('year', today.year, type=int)

    # 计算月份范围
    month_start = datetime(year, month, 1)
    if month == 12:
        month_end = datetime(year + 1, 1, 1)
    else:
        month_end = datetime(year, month + 1, 1)

    # 获取本月所有饮食记录
    records = DietRecord.query.filter(
        DietRecord.user_id == user.id,
        DietRecord.recorded_at >= month_start,
        DietRecord.recorded_at < month_end
    ).all()

    # 统计数据
    total_days = (month_end - month_start).days
    days_with_records = len(set(r.recorded_at.date() for r in records))
    total_calories = sum(r.calories for r in records)
    total_protein = sum(r.protein for r in records)
    total_carbs = sum(r.carbs for r in records)
    total_fat = sum(r.fat for r in records)

    target = user.target_calories or 1800
    avg_calories = round(total_calories / days_with_records) if days_with_records > 0 else 0

    # 按餐次统计
    by_meal = {}
    for r in records:
        meal = r.meal_type or 'other'
        if meal not in by_meal:
            by_meal[meal] = {'calories': 0, 'count': 0}
        by_meal[meal]['calories'] += r.calories
        by_meal[meal]['count'] += 1

    # 按日期统计热量
    daily_calories = {}
    for r in records:
        date_str = r.recorded_at.strftime('%Y-%m-%d')
        if date_str not in daily_calories:
            daily_calories[date_str] = 0
        daily_calories[date_str] += r.calories

    # 计算达标天数
    on_target_days = sum(1 for cal in daily_calories.values() if cal <= target * 1.1 and cal >= target * 0.8)

    return jsonify({
        'year': year,
        'month': month,
        'totalDays': total_days,
        'recordDays': days_with_records,
        'totalCalories': total_calories,
        'avgCalories': avg_calories,
        'targetCalories': target,
        'onTargetDays': on_target_days,
        'totalProtein': round(total_protein, 1),
        'totalCarbs': round(total_carbs, 1),
        'totalFat': round(total_fat, 1),
        'byMeal': by_meal,
        'dailyCalories': daily_calories,
    })


@diet_bp.route('/nutrition-breakdown', methods=['GET'])
def nutrition_breakdown():
    """营养素占比分析"""
    user = get_current_user()
    if not user:
        return jsonify({'success': False, 'message': '未登录'}), 401

    days = request.args.get('days', 7, type=int)
    start_date = datetime.utcnow() - timedelta(days=days)

    records = DietRecord.query.filter(
        DietRecord.user_id == user.id,
        DietRecord.recorded_at >= start_date
    ).all()

    total_calories = sum(r.calories for r in records)
    total_protein = sum(r.protein for r in records)
    total_carbs = sum(r.carbs for r in records)
    total_fat = sum(r.fat for r in records)

    # 计算各营养素提供的热量
    protein_cal = total_protein * 4  # 蛋白质每克4卡
    carbs_cal = total_carbs * 4      # 碳水每克4卡
    fat_cal = total_fat * 9          # 脂肪每克9卡

    # 计算占比
    if total_calories > 0:
        protein_pct = round(protein_cal / total_calories * 100)
        carbs_pct = round(carbs_cal / total_calories * 100)
        fat_pct = round(fat_cal / total_calories * 100)
    else:
        protein_pct = carbs_pct = fat_pct = 0

    return jsonify({
        'days': days,
        'totalCalories': total_calories,
        'protein': {
            'grams': round(total_protein, 1),
            'calories': round(protein_cal),
            'percentage': protein_pct,
        },
        'carbs': {
            'grams': round(total_carbs, 1),
            'calories': round(carbs_cal),
            'percentage': carbs_pct,
        },
        'fat': {
            'grams': round(total_fat, 1),
            'calories': round(fat_cal),
            'percentage': fat_pct,
        },
        'recommended': {
            'protein': '10-35%',
            'carbs': '45-65%',
            'fat': '20-35%',
        }
    })
