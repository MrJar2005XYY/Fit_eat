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
    foods = Food.query.filter(Food.id.in_(food_ids)).all() if food_ids else []
    return jsonify([f.to_dict() for f in foods])
