from flask import Blueprint, jsonify, request
from models.food import Food

discover_bp = Blueprint('discover', __name__)


@discover_bp.route('/ingredients', methods=['GET'])
def get_ingredients():
    """获取食材百科"""
    limit = request.args.get('limit', 6, type=int)

    # 从食物库中随机选择食材作为百科内容
    foods = Food.query.order_by(func.random()).limit(limit).all()

    # 构建材食百科数据
    ingredients = []
    for food in foods:
        # 根据食物特点设置益处
        benefits = []
        if food.protein > 15:
            benefits.append('高蛋白')
        if food.fat < 10:
            benefits.append('低脂')
        if food.fiber > 3:
            benefits.append('高纤维')
        if food.carbs < 20:
            benefits.append('低碳水')
        if not benefits:
            benefits.append('营养均衡')

        ingredients.append({
            'id': food.id,
            'name': food.name,
            'benefit': '、'.join(benefits[:2]),
            'image': food.image,
            'calories': food.calories,
            'protein': food.protein,
        })

    return jsonify(ingredients)


@discover_bp.route('/articles', methods=['GET'])
def get_articles():
    """获取健康知识文章"""
    # 基于食物库生成健康知识
    articles = [
        {
            'id': 1,
            'title': '减脂期间如何正确摄入碳水？',
            'desc': '优质碳水 vs 精制碳水，选对才能瘦得快。',
            'icon': 'grain',
            'color': 'orange',
            'content': '选择全谷物、薯类等复合碳水，避免精制糖和白面包。每餐碳水占比控制在40-50%。'
        },
        {
            'id': 2,
            'title': '蛋白质摄入量计算指南',
            'desc': '体重 × 1.5-2g，运动人群需要更多。',
            'icon': 'fitness_center',
            'color': 'blue',
            'content': '普通人群每天每公斤体重摄入1.2-1.5g蛋白质，运动人群需要1.5-2g。'
        },
        {
            'id': 3,
            'title': '8种高饱腹感低热量食物',
            'desc': '吃饱也能瘦，关键是选对食材。',
            'icon': 'local_fire_department',
            'color': 'red',
            'content': '鸡胸肉、西兰花、黄瓜、番茄、菠菜、蘑菇、豆腐、鸡蛋白都是高饱腹感低热量的好选择。'
        },
        {
            'id': 4,
            'title': 'Omega-3脂肪酸的重要性',
            'desc': '为什么营养师都推荐每周吃两次鱼？',
            'icon': 'spa',
            'color': 'green',
            'content': 'Omega-3有助于降低炎症、保护心血管、促进大脑健康。深海鱼、亚麻籽、核桃都是良好来源。'
        },
        {
            'id': 5,
            'title': '膳食纤维的神奇功效',
            'desc': '每天25g纤维，肠道健康的基础。',
            'icon': 'grass',
            'color': 'green',
            'content': '膳食纤维促进肠道蠕动、降低胆固醇、稳定血糖。蔬菜、水果、全谷物都是良好来源。'
        },
    ]

    return jsonify(articles)


@discover_bp.route('/daily-tip', methods=['GET'])
def get_daily_tip():
    """获取每日一贴"""
    import random
    from datetime import date

    tips = [
        '早餐摄入全天30%的热量，能有效提升上午的代谢率。建议搭配蛋白质+复合碳水+少量健康脂肪。',
        '每天饮水2000ml以上，餐前喝一杯水可以增加饱腹感，减少正餐摄入量约15%。',
        '减脂期间不必完全戒糖，适量天然果糖（水果）是安全的。但要避免添加糖和含糖饮料。',
        '蔬菜占每餐的一半以上，既增加饱腹感又提供丰富的维生素和矿物质，热量却极低。',
        '晚上8点后进食不会直接导致发胖，关键是全天总热量。但如果容易暴食，建议设定进食时间窗口。',
        '蛋白质的食物热效应最高，消化蛋白质本身就会消耗热量。每餐都要有优质蛋白来源。',
        '运动后30分钟内补充蛋白质和碳水，有助于肌肉恢复和糖原补充。',
        '睡眠不足会影响瘦素分泌，增加食欲。保证每天7-8小时的优质睡眠。',
        '细嚼慢咽能让大脑有时间接收饱腹信号，一般建议每口食物咀嚼20-30次。',
        '记录饮食是减脂的有效工具，能帮助你了解真实的摄入情况，避免无意识进食。',
    ]

    # 使用日期作为种子，确保每天显示不同的提示
    today = date.today()
    index = today.toordinal() % len(tips)

    return jsonify({
        'tip': tips[index],
        'date': today.strftime('%Y-%m-%d'),
    })


@discover_bp.route('/tags', methods=['GET'])
def get_tags():
    """获取热门标签"""
    tags = [
        {'name': '高蛋白', 'count': 0},
        {'name': '低脂', 'count': 0},
        {'name': '低碳水', 'count': 0},
        {'name': '高纤维', 'count': 0},
        {'name': '减脂', 'count': 0},
        {'name': '增肌', 'count': 0},
        {'name': '早餐', 'count': 0},
        {'name': '午餐', 'count': 0},
        {'name': '晚餐', 'count': 0},
        {'name': '加餐', 'count': 0},
    ]

    # 统计每个标签的食物数量
    for tag in tags:
        tag['count'] = Food.query.filter(Food.tags.contains(tag['name'])).count()

    # 按数量排序
    tags.sort(key=lambda x: x['count'], reverse=True)

    return jsonify(tags)


# 需要导入func
from sqlalchemy import func
