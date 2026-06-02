from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, session
from sqlalchemy import func
from models import db
from models.user import User
from models.exercise import ExerciseType, ExerciseRecord

exercise_bp = Blueprint('exercise', __name__)


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


@exercise_bp.route('/types', methods=['GET'])
def get_exercise_types():
    """获取所有运动类型"""
    category = request.args.get('category', '')
    query = ExerciseType.query
    if category:
        query = query.filter_by(category=category)
    types = query.order_by(ExerciseType.category, ExerciseType.name).all()
    return jsonify([t.to_dict() for t in types])


@exercise_bp.route('/records', methods=['GET'])
def get_records():
    """获取运动记录"""
    user = get_current_user()
    if not user:
        return jsonify({'success': False, 'message': '未登录'}), 401

    date = request.args.get('date')
    query = ExerciseRecord.query.filter_by(user_id=user.id)

    if date:
        try:
            d = datetime.strptime(date, '%Y-%m-%d')
            query = query.filter(
                ExerciseRecord.recorded_at >= d,
                ExerciseRecord.recorded_at < d + timedelta(days=1)
            )
        except ValueError:
            pass

    records = query.order_by(ExerciseRecord.recorded_at.desc()).all()
    return jsonify([r.to_dict() for r in records])


@exercise_bp.route('/records', methods=['POST'])
def add_record():
    """添加运动记录"""
    user = get_current_user()
    if not user:
        return jsonify({'success': False, 'message': '未登录'}), 401

    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': '请求数据无效'}), 400

    exercise_type_id = data.get('exerciseTypeId')
    duration = data.get('duration', 0)
    calories = data.get('calories', 0)
    distance = data.get('distance', 0)
    heart_rate = data.get('heartRate', 0)
    notes = data.get('notes', '')

    # 如果有运动类型ID，自动计算消耗
    exercise_type = None
    if exercise_type_id:
        exercise_type = ExerciseType.query.get(exercise_type_id)
        if exercise_type and calories == 0:
            # 卡路里 = MET * 体重(kg) * 时间(小时)
            weight = user.weight or 60
            calories = int(exercise_type.met * weight * (duration / 60))

    record = ExerciseRecord(
        user_id=user.id,
        exercise_type_id=exercise_type_id,
        exercise_name=data.get('name', exercise_type.name if exercise_type else ''),
        duration=duration,
        calories=calories,
        distance=distance,
        heart_rate=heart_rate,
        notes=notes,
    )
    db.session.add(record)
    db.session.commit()

    return jsonify({'success': True, 'id': record.id, 'calories': calories})


@exercise_bp.route('/records/<int:record_id>', methods=['DELETE'])
def delete_record(record_id):
    """删除运动记录"""
    user = get_current_user()
    if not user:
        return jsonify({'success': False, 'message': '未登录'}), 401

    record = ExerciseRecord.query.filter_by(id=record_id, user_id=user.id).first()
    if not record:
        return jsonify({'success': False, 'message': '记录不存在'}), 404

    db.session.delete(record)
    db.session.commit()
    return jsonify({'success': True})


@exercise_bp.route('/today-summary', methods=['GET'])
def today_summary():
    """获取今日运动摘要"""
    user = get_current_user()
    if not user:
        return jsonify({'success': False, 'message': '未登录'}), 401

    start, end = today_range()
    records = ExerciseRecord.query.filter(
        ExerciseRecord.user_id == user.id,
        ExerciseRecord.recorded_at >= start,
        ExerciseRecord.recorded_at < end
    ).all()

    total_duration = sum(r.duration for r in records)
    total_calories = sum(r.calories for r in records)
    total_distance = sum(r.distance for r in records)

    return jsonify({
        'duration': total_duration,
        'calories': total_calories,
        'distance': round(total_distance, 2),
        'count': len(records),
        'records': [r.to_dict() for r in records],
    })


@exercise_bp.route('/weekly-summary', methods=['GET'])
def weekly_summary():
    """获取本周运动摘要"""
    user = get_current_user()
    if not user:
        return jsonify({'success': False, 'message': '未登录'}), 401

    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    weekday = today.weekday()
    week_start = today - timedelta(days=weekday)

    days = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
    result = []

    for i in range(7):
        day_start = week_start + timedelta(days=i)
        day_end = day_start + timedelta(days=1)
        records = ExerciseRecord.query.filter(
            ExerciseRecord.user_id == user.id,
            ExerciseRecord.recorded_at >= day_start,
            ExerciseRecord.recorded_at < day_end
        ).all()

        result.append({
            'day': days[i],
            'duration': sum(r.duration for r in records),
            'calories': sum(r.calories for r in records),
            'count': len(records),
        })

    return jsonify(result)


@exercise_bp.route('/monthly-summary', methods=['GET'])
def monthly_summary():
    """获取本月运动摘要"""
    user = get_current_user()
    if not user:
        return jsonify({'success': False, 'message': '未登录'}), 401

    today = datetime.utcnow()
    month_start = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    if today.month == 12:
        next_month = today.replace(year=today.year + 1, month=1, day=1)
    else:
        next_month = today.replace(month=today.month + 1, day=1)

    records = ExerciseRecord.query.filter(
        ExerciseRecord.user_id == user.id,
        ExerciseRecord.recorded_at >= month_start,
        ExerciseRecord.recorded_at < next_month
    ).all()

    total_duration = sum(r.duration for r in records)
    total_calories = sum(r.calories for r in records)
    total_distance = sum(r.distance for r in records)

    # 按运动类型分组
    by_type = {}
    for r in records:
        name = r.exercise_name or '其他'
        if name not in by_type:
            by_type[name] = {'duration': 0, 'calories': 0, 'count': 0}
        by_type[name]['duration'] += r.duration
        by_type[name]['calories'] += r.calories
        by_type[name]['count'] += 1

    return jsonify({
        'totalDuration': total_duration,
        'totalCalories': total_calories,
        'totalDistance': round(total_distance, 2),
        'totalCount': len(records),
        'byType': by_type,
    })
