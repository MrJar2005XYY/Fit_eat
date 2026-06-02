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


@health_bp.route('/report', methods=['GET'])
def get_report():
    """生成健康报告"""
    user = get_current_user()
    if not user:
        return jsonify({'success': False, 'message': '未登录'}), 401

    days = request.args.get('days', 7, type=int)
    start_date = datetime.utcnow() - timedelta(days=days)

    # 获取各类健康记录
    records = HealthRecord.query.filter(
        HealthRecord.user_id == user.id,
        HealthRecord.recorded_at >= start_date
    ).all()

    # 按类型分组
    by_type = {}
    for r in records:
        if r.record_type not in by_type:
            by_type[r.record_type] = []
        by_type[r.record_type].append(r)

    # 生成报告数据
    report = {
        'period': f'最近{days}天',
        'startDate': start_date.strftime('%Y-%m-%d'),
        'endDate': datetime.utcnow().strftime('%Y-%m-%d'),
        'metrics': {},
    }

    # 体重趋势
    if 'weight' in by_type:
        weight_records = by_type['weight']
        weight_values = [r.value for r in weight_records]
        report['metrics']['weight'] = {
            'current': weight_values[-1] if weight_values else 0,
            'min': min(weight_values) if weight_values else 0,
            'max': max(weight_values) if weight_values else 0,
            'avg': round(sum(weight_values) / len(weight_values), 1) if weight_values else 0,
            'change': round(weight_values[-1] - weight_values[0], 1) if len(weight_values) > 1 else 0,
            'trend': 'down' if len(weight_values) > 1 and weight_values[-1] < weight_values[0] else 'up',
            'count': len(weight_values),
        }

    # 体脂趋势
    if 'body_fat' in by_type:
        bf_records = by_type['body_fat']
        bf_values = [r.value for r in bf_records]
        report['metrics']['bodyFat'] = {
            'current': bf_values[-1] if bf_values else 0,
            'min': min(bf_values) if bf_values else 0,
            'max': max(bf_values) if bf_values else 0,
            'avg': round(sum(bf_values) / len(bf_values), 1) if bf_values else 0,
            'change': round(bf_values[-1] - bf_values[0], 1) if len(bf_values) > 1 else 0,
            'count': len(bf_values),
        }

    # 血糖趋势
    if 'blood_sugar' in by_type:
        bs_records = by_type['blood_sugar']
        bs_values = [r.value for r in bs_records]
        report['metrics']['bloodSugar'] = {
            'current': bs_values[-1] if bs_values else 0,
            'min': min(bs_values) if bs_values else 0,
            'max': max(bs_values) if bs_values else 0,
            'avg': round(sum(bs_values) / len(bs_values), 1) if bs_values else 0,
            'count': len(bs_values),
            'status': 'normal' if bs_values and 3.9 <= bs_values[-1] <= 6.1 else 'warning',
        }

    # 血压趋势
    if 'blood_pressure' in by_type:
        bp_records = by_type['blood_pressure']
        report['metrics']['bloodPressure'] = {
            'current': {
                'systolic': bp_records[-1].value if bp_records else 0,
                'diastolic': bp_records[-1].value2 if bp_records else 0,
            },
            'count': len(bp_records),
            'status': 'normal' if bp_records and bp_records[-1].value < 140 and bp_records[-1].value2 < 90 else 'warning',
        }

    # 计算BMI
    height = user.height or 0
    weight = report['metrics'].get('weight', {}).get('current', user.weight or 0)
    bmi = round(weight / ((height / 100) ** 2), 1) if height > 0 and weight > 0 else 0
    report['bmi'] = bmi

    # BMI状态
    if bmi < 18.5:
        report['bmiStatus'] = '偏瘦'
        report['bmiAdvice'] = '建议适当增加营养摄入'
    elif bmi < 24:
        report['bmiStatus'] = '正常'
        report['bmiAdvice'] = '继续保持健康的生活方式'
    elif bmi < 28:
        report['bmiStatus'] = '偏胖'
        report['bmiAdvice'] = '建议控制饮食，增加运动'
    else:
        report['bmiStatus'] = '肥胖'
        report['bmiAdvice'] = '建议咨询医生制定减重计划'

    # 记录统计
    report['recordStats'] = {
        'totalRecords': len(records),
        'byType': {k: len(v) for k, v in by_type.items()},
    }

    return jsonify(report)
