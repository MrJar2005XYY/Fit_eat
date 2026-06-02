from flask import Blueprint, request, jsonify, session
from models import db
from models.user import User

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': '请求数据无效'}), 400
    account_id = data.get('accountId', '').strip()
    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '')

    if not account_id or not username or not email or not password:
        return jsonify({'success': False, 'message': '请填写完整信息'}), 400

    if User.query.filter_by(account_id=account_id).first():
        return jsonify({'success': False, 'message': '账户ID已存在'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'success': False, 'message': '邮箱已注册'}), 400

    user = User(account_id=account_id, username=username, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    session['user_id'] = user.id
    return jsonify({'success': True, 'token': f'user_{user.id}'})


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': '请求数据无效'}), 400
    account_id = data.get('accountId', '').strip()
    password = data.get('password', '')

    user = User.query.filter_by(account_id=account_id).first()
    if not user or not user.check_password(password):
        return jsonify({'success': False, 'message': '账户ID或密码错误'}), 401

    session['user_id'] = user.id
    return jsonify({'success': True, 'token': f'user_{user.id}'})


@auth_bp.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return jsonify({'success': True})
