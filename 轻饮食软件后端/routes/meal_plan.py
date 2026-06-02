from datetime import datetime, timedelta, date
from flask import Blueprint, request, jsonify, session
from models import db
from models.user import User
from models.food import Food
from models.meal_plan import MealPlan, MealPlanItem

meal_plan_bp = Blueprint('meal_plan', __name__)


def get_current_user():
    user_id = session.get('user_id')
    if not user_id:
        return None
    return User.query.get(user_id)


@meal_plan_bp.route('/plans', methods=['GET'])
def get_plans():
    """获取用户的饮食计划列表"""
    user = get_current_user()
    if not user:
        return jsonify({'success': False, 'message': '未登录'}), 401

    plans = MealPlan.query.filter_by(user_id=user.id).order_by(MealPlan.created_at.desc()).all()
    return jsonify([p.to_dict() for p in plans])


@meal_plan_bp.route('/plans', methods=['POST'])
def create_plan():
    """创建饮食计划"""
    user = get_current_user()
    if not user:
        return jsonify({'success': False, 'message': '未登录'}), 401

    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': '请求数据无效'}), 400

    start_date = datetime.strptime(data.get('startDate', ''), '%Y-%m-%d').date()
    end_date = datetime.strptime(data.get('endDate', ''), '%Y-%m-%d').date()

    plan = MealPlan(
        user_id=user.id,
        name=data.get('name', f'饮食计划 {start_date}'),
        start_date=start_date,
        end_date=end_date,
        target_calories=data.get('targetCalories', user.target_calories or 1800),
        notes=data.get('notes', ''),
    )
    db.session.add(plan)
    db.session.commit()

    return jsonify({'success': True, 'id': plan.id})


@meal_plan_bp.route('/plans/<int:plan_id>', methods=['GET'])
def get_plan(plan_id):
    """获取饮食计划详情"""
    user = get_current_user()
    if not user:
        return jsonify({'success': False, 'message': '未登录'}), 401

    plan = MealPlan.query.filter_by(id=plan_id, user_id=user.id).first()
    if not plan:
        return jsonify({'success': False, 'message': '计划不存在'}), 404

    return jsonify(plan.to_dict(include_items=True))


@meal_plan_bp.route('/plans/<int:plan_id>', methods=['DELETE'])
def delete_plan(plan_id):
    """删除饮食计划"""
    user = get_current_user()
    if not user:
        return jsonify({'success': False, 'message': '未登录'}), 401

    plan = MealPlan.query.filter_by(id=plan_id, user_id=user.id).first()
    if not plan:
        return jsonify({'success': False, 'message': '计划不存在'}), 404

    db.session.delete(plan)
    db.session.commit()
    return jsonify({'success': True})


@meal_plan_bp.route('/plans/<int:plan_id>/items', methods=['POST'])
def add_item(plan_id):
    """添加计划项目"""
    user = get_current_user()
    if not user:
        return jsonify({'success': False, 'message': '未登录'}), 401

    plan = MealPlan.query.filter_by(id=plan_id, user_id=user.id).first()
    if not plan:
        return jsonify({'success': False, 'message': '计划不存在'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': '请求数据无效'}), 400

    food_id = data.get('foodId')
    calories = data.get('calories', 0)
    protein = data.get('protein', 0)
    carbs = data.get('carbs', 0)
    fat = data.get('fat', 0)

    # 如果有食物ID，从食物库获取营养数据
    if food_id:
        food = Food.query.get(food_id)
        if food:
            amount = data.get('amount', 1.0)
            calories = int(food.calories * amount)
            protein = round(food.protein * amount, 1)
            carbs = round(food.carbs * amount, 1)
            fat = round(food.fat * amount, 1)

    item = MealPlanItem(
        plan_id=plan_id,
        food_id=food_id,
        food_name=data.get('name', ''),
        meal_type=data.get('mealType', ''),
        day_of_week=data.get('dayOfWeek', 0),
        calories=calories,
        protein=protein,
        carbs=carbs,
        fat=fat,
        amount=data.get('amount', 1.0),
    )
    db.session.add(item)
    db.session.commit()

    return jsonify({'success': True, 'id': item.id})


@meal_plan_bp.route('/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    """删除计划项目"""
    user = get_current_user()
    if not user:
        return jsonify({'success': False, 'message': '未登录'}), 401

    item = MealPlanItem.query.get(item_id)
    if not item:
        return jsonify({'success': False, 'message': '项目不存在'}), 404

    plan = MealPlan.query.filter_by(id=item.plan_id, user_id=user.id).first()
    if not plan:
        return jsonify({'success': False, 'message': '无权操作'}), 403

    db.session.delete(item)
    db.session.commit()
    return jsonify({'success': True})


@meal_plan_bp.route('/items/<int:item_id>/complete', methods=['POST'])
def toggle_complete(item_id):
    """标记计划项目完成/未完成"""
    user = get_current_user()
    if not user:
        return jsonify({'success': False, 'message': '未登录'}), 401

    item = MealPlanItem.query.get(item_id)
    if not item:
        return jsonify({'success': False, 'message': '项目不存在'}), 404

    plan = MealPlan.query.filter_by(id=item.plan_id, user_id=user.id).first()
    if not plan:
        return jsonify({'success': False, 'message': '无权操作'}), 403

    item.is_completed = not item.is_completed
    item.completed_at = datetime.utcnow() if item.is_completed else None
    db.session.commit()

    return jsonify({'success': True, 'isCompleted': item.is_completed})


@meal_plan_bp.route('/current', methods=['GET'])
def get_current_plan():
    """获取当前进行中的饮食计划"""
    user = get_current_user()
    if not user:
        return jsonify({'success': False, 'message': '未登录'}), 401

    today = date.today()
    plan = MealPlan.query.filter(
        MealPlan.user_id == user.id,
        MealPlan.start_date <= today,
        MealPlan.end_date >= today
    ).order_by(MealPlan.created_at.desc()).first()

    if not plan:
        return jsonify(None)

    return jsonify(plan.to_dict(include_items=True))
