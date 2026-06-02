from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, session
from sqlalchemy import func
from models import db
from models.user import User
from models.health import HealthRecord

health_bp = Blueprint('health', __name__)


def get_current_user():
    user_id = session.get('user_id')
    if not user_id:
        return None
    return User.query.get(user_id)


@health_bp.route('/records', methods=['GET'])
def get_records():
    """获取健康记录"""
    user = get_current_user()
    if not user:
        return jsonify({'success': False, 'message': '未登录'}), 401

    record_type = request.args.get('type', '')
    limit = request.args.get('limit', 30, type=int)

    query = HealthRecord.query.filter_by(user_id=user.id)
    if record_type:
        query = query.filter_by(record_type=record_type)

    records = query.order_by(HealthRecord.recorded_at.desc()).limit(limit).all()
    return jsonify([r.to_dict() for r in records])


@health_bp.route('/records', methods=['POST'])
def add_record():
    """添加健康记录"""
    user = get_current_user()
    if not user:
        return jsonify({'success': False, 'message': '未登录'}), 401

    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': '请求数据无效'}), 400

    record_type = data.get('type', '')
    value = data.get('value', 0)
    value2 = data.get('value2', 0)

    # 设置单位
    units = {
        'weight': 'kg',
        'body_fat': '%',
        'blood_sugar': 'mmol/L',
        'blood_pressure': 'mmHg',
        'waist': 'cm',
        'hip': 'cm',
        'arm': 'cm',
    }
    unit = units.get(record_type, '')

    record = HealthRecord(
        user_id=user.id,
        record_type=record_type,
        value=value,
        value2=value2,
        unit=unit,
        notes=data.get('notes', ''),
    )
    db.session.add(record)

    # 如果是体重记录，同步更新用户体重
    if record_type == 'weight' and value > 0:
        user.weight = value
    elif record_type == 'body_fat' and value > 0:
        user.body_fat = value

    db.session.commit()

    return jsonify({'success': True, 'id': record.id})


@health_bp.route('/records/<int:record_id>', methods=['DELETE'])
def delete_record(record_id):
    """删除健康记录"""
    user = get_current_user()
    if not user:
        return jsonify({'success': False, 'message': '未登录'}), 401

    record = HealthRecord.query.filter_by(id=record_id, user_id=user.id).first()
    if not record:
        return jsonify({'success': False, 'message': '记录不存在'}), 404

    db.session.delete(record)
    db.session.commit()
    return jsonify({'success': True})


@health_bp.route('/trends', methods=['GET'])
def get_trends():
    """获取健康数据趋势"""
    user = get_current_user()
    if not user:
        return jsonify({'success': False, 'message': '未登录'}), 401

    record_type = request.args.get('type', 'weight')
    days = request.args.get('days', 30, type=int)

    start_date = datetime.utcnow() - timedelta(days=days)
    records = HealthRecord.query.filter(
        HealthRecord.user_id == user.id,
        HealthRecord.record_type == record_type,
        HealthRecord.recorded_at >= start_date
    ).order_by(HealthRecord.recorded_at.asc()).all()

    return jsonify({
        'type': record_type,
        'records': [r.to_dict() for r in records],
        'latest': records[-1].to_dict() if records else None,
        'min': min(r.value for r in records) if records else 0,
        'max': max(r.value for r in records) if records else 0,
        'avg': round(sum(r.value for r in records) / len(records), 1) if records else 0,
    })


@health_bp.route('/summary', methods=['GET'])
def get_summary():
    """获取健康数据摘要"""
    user = get_current_user()
    if not user:
        return jsonify({'success': False, 'message': '未登录'}), 401

    # 获取最新的各类记录
    latest = {}
    for record_type in ['weight', 'body_fat', 'blood_sugar', 'blood_pressure', 'waist', 'hip', 'arm']:
        record = HealthRecord.query.filter_by(
            user_id=user.id,
            record_type=record_type
        ).order_by(HealthRecord.recorded_at.desc()).first()
        if record:
            latest[record_type] = record.to_dict()

    # 计算BMI
    weight = latest.get('weight', {}).get('value', user.weight or 0)
    height = user.height or 0
    bmi = round(weight / ((height / 100) ** 2), 1) if height > 0 and weight > 0 else 0

    return jsonify({
        'latest': latest,
        'bmi': bmi,
        'height': height,
        'targetWeight': user.target_weight or 0,
    })
