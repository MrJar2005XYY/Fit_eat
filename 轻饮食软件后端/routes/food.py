from flask import Blueprint, request, jsonify, session
from models import db
from models.food import Food
from models.community import Favorite

food_bp = Blueprint('food', __name__)


@food_bp.route('/list', methods=['GET'])
def get_list():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    meal_type = request.args.get('meal_type', '')

    query = Food.query
    if meal_type and meal_type != 'all':
        query = query.filter_by(meal_type=meal_type)

    # 优先显示有图片的食谱
    from sqlalchemy import case
    has_image = case((Food.image != '', 0), else_=1)
    pagination = query.order_by(has_image, Food.id.desc()).paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({
        'items': [f.to_dict() for f in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'page': page
    })


@food_bp.route('/<int:food_id>', methods=['GET'])
def get_detail(food_id):
    food = Food.query.get(food_id)
    if not food:
        return jsonify({'success': False, 'message': '食物不存在'}), 404
    return jsonify(food.to_dict())


@food_bp.route('/search', methods=['GET'])
def search():
    q = request.args.get('q', '').strip()
    if not q:
        foods = Food.query.limit(20).all()
    else:
        foods = Food.query.filter(Food.name.contains(q)).limit(20).all()
    return jsonify([f.to_dict() for f in foods])


@food_bp.route('/<int:food_id>/favorite', methods=['POST'])
def toggle_favorite(food_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': '未登录'}), 401

    food = Food.query.get(food_id)
    if not food:
        return jsonify({'success': False, 'message': '食物不存在'}), 404

    existing = Favorite.query.filter_by(user_id=user_id, food_id=food_id).first()
    if existing:
        db.session.delete(existing)
        db.session.commit()
        return jsonify({'success': True, 'isFavorite': False})
    else:
        fav = Favorite(user_id=user_id, food_id=food_id)
        db.session.add(fav)
        db.session.commit()
        return jsonify({'success': True, 'isFavorite': True})


@food_bp.route('/favorites', methods=['GET'])
def get_favorites():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify([])

    favs = Favorite.query.filter_by(user_id=user_id).order_by(Favorite.created_at.desc()).all()
    food_ids = [f.food_id for f in favs]
    if not food_ids:
        return jsonify([])

    foods = Food.query.filter(Food.id.in_(food_ids)).all()
    food_map = {f.id: f for f in foods}
    ordered_foods = [food_map[fid] for fid in food_ids if fid in food_map]
    return jsonify([f.to_dict() for f in ordered_foods])


@food_bp.route('/<int:food_id>/similar', methods=['GET'])
def get_similar(food_id):
    """获取相似食物推荐"""
    food = Food.query.get(food_id)
    if not food:
        return jsonify({'success': False, 'message': '食物不存在'}), 404

    limit = request.args.get('limit', 6, type=int)

    # 基于同餐次、同标签推荐相似食物
    similar_foods = []

    # 1. 优先推荐同餐次的食物
    if food.meal_type:
        same_meal = Food.query.filter(
            Food.meal_type == food.meal_type,
            Food.id != food_id
        ).limit(limit * 2).all()
        similar_foods.extend(same_meal)

    # 2. 如果有tags，推荐有相同tags的食物
    if food.tags:
        food_tags = [t.strip() for t in food.tags.split(',') if t.strip()]
        for tag in food_tags[:2]:  # 只取前两个标签
            tag_foods = Food.query.filter(
                Food.tags.contains(tag),
                Food.id != food_id,
                ~Food.id.in_([f.id for f in similar_foods])
            ).limit(limit).all()
            similar_foods.extend(tag_foods)

    # 3. 如果还不够，补充热量相近的食物
    if len(similar_foods) < limit:
        calorie_range = 100
        nearby_foods = Food.query.filter(
            Food.calories.between(food.calories - calorie_range, food.calories + calorie_range),
            Food.id != food_id,
            ~Food.id.in_([f.id for f in similar_foods])
        ).limit(limit - len(similar_foods)).all()
        similar_foods.extend(nearby_foods)

    # 去重并限制数量
    seen = set()
    result = []
    for f in similar_foods:
        if f.id not in seen:
            seen.add(f.id)
            result.append(f.to_dict())
        if len(result) >= limit:
            break

    return jsonify(result)


@food_bp.route('/recommend', methods=['GET'])
def get_recommend():
    """智能推荐食物"""
    user_id = session.get('user_id')
    meal_type = request.args.get('meal', '')
    limit = request.args.get('limit', 6, type=int)

    query = Food.query

    # 如果指定了餐次，优先推荐该餐次的食物
    if meal_type:
        query = query.filter_by(meal_type=meal_type)

    # 优先推荐高蛋白、低热量的食物
    from sqlalchemy import case
    score = case(
        (Food.protein > 15, 3),
        (Food.protein > 10, 2),
        else_=1
    ) - case(
        (Food.calories > 500, 2),
        (Food.calories > 300, 1),
        else_=0
    )

    # 如果用户已登录，排除已收藏的食物
    if user_id:
        fav_food_ids = [f.food_id for f in Favorite.query.filter_by(user_id=user_id).all()]
        if fav_food_ids:
            query = query.filter(~Food.id.in_(fav_food_ids))

    foods = query.order_by(score.desc()).limit(limit).all()
    return jsonify([f.to_dict() for f in foods])
