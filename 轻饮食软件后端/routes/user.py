from flask import Blueprint, request, jsonify, session
from models import db
from models.user import User

user_bp = Blueprint('user', __name__)


def get_current_user():
    user_id = session.get('user_id')
    if not user_id:
        return None
    return User.query.get(user_id)


@user_bp.route('/profile', methods=['GET'])
def get_profile():
    user = get_current_user()
    if not user:
        return jsonify({'success': False, 'message': '未登录'}), 401
    return jsonify(user.to_dict())


@user_bp.route('/profile', methods=['PUT'])
def update_profile():
    user = get_current_user()
    if not user:
        return jsonify({'success': False, 'message': '未登录'}), 401

    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': '请求数据无效'}), 400
    if 'username' in data:
        user.username = data['username']
    if 'avatar' in data:
        user.avatar = data['avatar']
    if 'bio' in data:
        user.bio = data['bio']
    if 'gender' in data:
        user.gender = data['gender']
    if 'age' in data:
        user.age = data['age']
    if 'height' in data:
        user.height = data['height']
    if 'weight' in data:
        user.weight = data['weight']
    if 'body_fat' in data:
        user.body_fat = data['body_fat']
    if 'target_weight' in data:
        user.target_weight = data['target_weight']
    if 'target_calories' in data:
        user.target_calories = data['target_calories']

    db.session.commit()
    return jsonify({'success': True, 'data': user.to_dict()})


@user_bp.route('/account-id', methods=['PUT'])
def update_account_id():
    user = get_current_user()
    if not user:
        return jsonify({'success': False, 'message': '未登录'}), 401

    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': '请求数据无效'}), 400
    new_account_id = data.get('accountId', '').strip()

    if not new_account_id:
        return jsonify({'success': False, 'message': '账户ID不能为空'}), 400

    if len(new_account_id) < 3:
        return jsonify({'success': False, 'message': '账户ID至少需要3个字符'}), 400

    if new_account_id == user.account_id:
        return jsonify({'success': False, 'message': '新账户ID与当前相同'}), 400

    existing = User.query.filter_by(account_id=new_account_id).first()
    if existing and existing.id != user.id:
        return jsonify({'success': False, 'message': '该账户ID已被使用'}), 400

    user.account_id = new_account_id
    db.session.commit()
    return jsonify({'success': True, 'data': user.to_dict()})


@user_bp.route('/password', methods=['PUT'])
def update_password():
    user = get_current_user()
    if not user:
        return jsonify({'success': False, 'message': '未登录'}), 401

    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': '请求数据无效'}), 400
    old_password = data.get('oldPassword', '')
    new_password = data.get('newPassword', '')

    if not old_password or not new_password:
        return jsonify({'success': False, 'message': '请填写完整信息'}), 400

    if not user.check_password(old_password):
        return jsonify({'success': False, 'message': '旧密码错误'}), 400

    if len(new_password) < 6:
        return jsonify({'success': False, 'message': '新密码至少需要6个字符'}), 400

    user.set_password(new_password)
    db.session.commit()
    return jsonify({'success': True, 'message': '密码修改成功'})
