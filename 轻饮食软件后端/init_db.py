import json
from datetime import datetime, timedelta
from app import create_app
from models import db
from models.user import User
from models.food import Food
from models.achievement import Achievement
from models.community import CommunityPost
from models.diet import DietRecord, WaterRecord
from models.exercise import ExerciseType

app = create_app()


def init_database(force=False):
    with app.app_context():
        import os
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'light_diet.db')

        if os.path.exists(db_path) and not force:
            print('数据库已存在，跳过初始化。如需重置数据库，请运行: python init_db.py --force')
            return

        db.drop_all()
        db.create_all()
        print('数据库表已创建')

        # 创建管理员用户
        admin = User(
            account_id='admin',
            username='管理员',
            email='admin@lightdiet.com',
            gender='女',
            age=25,
            height=165,
            weight=58,
            body_fat=22,
            target_calories=1800,
            target_weight=55,
            plan_days=42,
            bio='越自律，越自由 | 坚持轻食第 42 天'
        )
        admin.set_password('admin123')
        db.session.add(admin)

        # 创建示例用户
        user1 = User(
            account_id='linyouxue',
            username='林小悦',
            email='lin@example.com',
            gender='女',
            age=24,
            height=163,
            weight=55,
            target_calories=1600,
            target_weight=52,
            plan_days=30
        )
        user1.set_password('123456')
        db.session.add(user1)
        db.session.flush()  # 确保用户 ID 可用

        # 创建食物数据
        foods = [
            Food(
                name='牛油果水波蛋活力碗',
                description='这款活力碗完美平衡了优质脂肪、蛋白质和复合碳水，是开启元气满满一天的理想选择。',
                calories=345, protein=18, carbs=24, fat=12, fiber=6,
                tags='高蛋白,低GI',
                ingredients=json.dumps([
                    {'name': '熟透牛油果', 'amount': '1/2个'},
                    {'name': '新鲜鸡蛋', 'amount': '1枚'},
                    {'name': '全麦欧包', 'amount': '1片'},
                    {'name': '樱桃番茄', 'amount': '5-6个'}
                ]),
                steps=json.dumps([
                    {'title': '准备牛油果泥', 'desc': '将牛油果切开去核，取出果肉压碎。加入少许柠檬汁、海盐和黑胡椒，搅拌至质地顺滑。'},
                    {'title': '制作水波蛋', 'desc': '锅中烧开水，加入一勺白醋。用勺子在水中搅出一个旋涡，缓缓倒入打好的鸡蛋，微火煮3分钟。'},
                    {'title': '组装装盘', 'desc': '在烤好的欧包上抹上牛油果泥，放上水波蛋，点缀切开的樱桃番茄，撒上奇亚籽即可。'}
                ]),
                benefits='牛油果富含单不饱和脂肪酸，有助于心脏健康。水波蛋提供完整的氨基酸谱，促进肌肉修复。',
                prep_time='15分钟', difficulty='简单', meal_type='breakfast'
            ),
            Food(
                name='蓝莓坚果酸奶碗',
                description='高蛋白免煮早餐，蓝莓的抗氧化力搭配希腊酸奶的丰富蛋白质。',
                calories=320, protein=18, carbs=35, fat=12, fiber=5,
                tags='高蛋白,免煮',
                ingredients=json.dumps([
                    {'name': '希腊酸奶', 'amount': '200g'},
                    {'name': '新鲜蓝莓', 'amount': '50g'},
                    {'name': '混合坚果', 'amount': '20g'},
                    {'name': '蜂蜜', 'amount': '1茶匙'}
                ]),
                steps=json.dumps([
                    {'title': '准备酸奶底', 'desc': '将希腊酸奶倒入碗中。'},
                    {'title': '摆盘装饰', 'desc': '撒上蓝莓和坚果，淋上蜂蜜即可。'}
                ]),
                benefits='希腊酸奶富含蛋白质和益生菌，蓝莓是天然抗氧化剂。',
                prep_time='5分钟', difficulty='简单', meal_type='breakfast'
            ),
            Food(
                name='嫩煎鸡胸肉沙拉',
                description='低GI优质蛋白午餐，鸡胸肉搭配新鲜蔬菜。',
                calories=450, protein=35, carbs=20, fat=18, fiber=8,
                tags='低GI,优质脂',
                ingredients=json.dumps([
                    {'name': '鸡胸肉', 'amount': '150g'},
                    {'name': '混合生菜', 'amount': '100g'},
                    {'name': '樱桃番茄', 'amount': '6个'},
                    {'name': '橄榄油', 'amount': '1汤匙'}
                ]),
                steps=json.dumps([
                    {'title': '煎鸡胸肉', 'desc': '鸡胸肉用盐和黑胡椒腌制，中火煎至两面金黄。'},
                    {'title': '准备沙拉', 'desc': '生菜铺底，放上切片鸡胸肉和番茄。'},
                    {'title': '调味', 'desc': '淋上橄榄油和柠檬汁即可。'}
                ]),
                benefits='鸡胸肉是优质低脂蛋白来源，搭配蔬菜提供丰富纤维。',
                prep_time='20分钟', difficulty='简单', meal_type='lunch'
            ),
            Food(
                name='柠檬香煎三文鱼配芦笋',
                description='Omega-3丰富的晚餐选择，低碳水高蛋白。',
                calories=380, protein=28, carbs=12, fat=22, fiber=4,
                tags='Omega-3,低碳水',
                ingredients=json.dumps([
                    {'name': '三文鱼排', 'amount': '150g'},
                    {'name': '芦笋', 'amount': '100g'},
                    {'name': '柠檬', 'amount': '1/2个'},
                    {'name': '橄榄油', 'amount': '1汤匙'}
                ]),
                steps=json.dumps([
                    {'title': '煎三文鱼', 'desc': '三文鱼抹盐和黑胡椒，皮面朝下煎4分钟，翻面再煎2分钟。'},
                    {'title': '烤芦笋', 'desc': '芦笋抹橄榄油，撒盐，烤箱200度烤8分钟。'},
                    {'title': '装盘', 'desc': '三文鱼和芦笋装盘，挤上柠檬汁。'}
                ]),
                benefits='三文鱼富含Omega-3脂肪酸，有助于大脑和心脏健康。',
                prep_time='15分钟', difficulty='中等', meal_type='dinner'
            ),
            Food(
                name='混合坚果与苹果片',
                description='高纤维健康加餐，补充能量。',
                calories=180, protein=5, carbs=20, fat=10, fiber=4,
                tags='高纤维',
                ingredients=json.dumps([
                    {'name': '混合坚果', 'amount': '25g'},
                    {'name': '苹果', 'amount': '1个'}
                ]),
                steps=json.dumps([
                    {'title': '准备食材', 'desc': '苹果切片，搭配混合坚果即可食用。'}
                ]),
                benefits='坚果提供健康脂肪，苹果富含膳食纤维。',
                prep_time='3分钟', difficulty='简单', meal_type='snack'
            ),
            Food(
                name='香煎鸡胸肉暖沙拉',
                description='温暖的低GI午餐，适合秋冬季节。',
                calories=450, protein=35, carbs=25, fat=18, fiber=7,
                tags='低GI,优质脂',
                ingredients=json.dumps([
                    {'name': '鸡胸肉', 'amount': '150g'},
                    {'name': '藜麦', 'amount': '50g'},
                    {'name': '西兰花', 'amount': '80g'},
                    {'name': '甜椒', 'amount': '1/2个'}
                ]),
                steps=json.dumps([
                    {'title': '煮藜麦', 'desc': '藜麦加水煮15分钟至软烂。'},
                    {'title': '煎鸡胸肉', 'desc': '鸡胸肉煎至金黄切片。'},
                    {'title': '组合', 'desc': '藜麦铺底，放上鸡胸肉和蔬菜。'}
                ]),
                benefits='藜麦是完全蛋白来源，搭配鸡胸肉蛋白质加倍。',
                prep_time='25分钟', difficulty='中等', meal_type='lunch'
            ),
        ]
        db.session.add_all(foods)

        # 创建成就数据
        achievements = [
            Achievement(name='毅力萌芽', description='连续坚持 7 天', icon='local_fire_department', color='orange', condition_type='streak', condition_value=7),
            Achievement(name='美食品鉴', description='记录 50 顿健康餐', icon='restaurant_menu', color='green', condition_type='records', condition_value=50),
            Achievement(name='健康律动', description='体重初见成效', icon='ecg_heart', color='red', condition_type='weight', condition_value=1),
            Achievement(name='内心平静', description='完成首次冥想', icon='self_improvement', color='purple', condition_type='records', condition_value=1),
            Achievement(name='百日宗师', description='坚持 100 天', icon='trophy', color='yellow', condition_type='streak', condition_value=100),
            Achievement(name='社区红人', description='获得 1000 点赞', icon='celebration', color='pink', condition_type='community', condition_value=1000),
            Achievement(name='营养专家', description='解锁所有食谱', icon='nutrition', color='teal', condition_type='records', condition_value=100),
            Achievement(name='榜上有名', description='进入排行榜前 10', icon='social_leaderboard', color='blue', condition_type='community', condition_value=10),
        ]
        db.session.add_all(achievements)

        # 创建社区帖子
        posts = [
            CommunityPost(
                user_id=admin.id,
                content='坚持轻食第 42 天，体重已经下降了 3 公斤！分享一下今天的午餐：藜麦鸡胸肉沙拉，蛋白质满满，饱腹感超强。关键是要选对酱汁，我用的是橄榄油+柠檬汁+少许蜂蜜的自制酱，热量低又好吃。',
                image='https://lh3.googleusercontent.com/aida-public/AB6AXuBL22umvGsNCB29_UWSHOsvz3kAZT1Er0GAiWiKDgMOnPloyGMkPtgtdE6KjW_dOyCsGRTj4keyazSBCis4YOmau38boWMntEEUjBQkd_4B9g49WUTQPbbkPdQELD2EGEsW-aalvMmLoffgQThhIDjWxOdvhSQNwNSf2A0abZD-y3YT8ccaLtsx7JxgcOksZes8xJxTTSM4Q9UWIxn_MTLEykY4hF0X34MWPFmdjr76BYHhl78mG1WtgflGY7_dP35J2THL8BUE8gs7',
                category='recipe'
            ),
            CommunityPost(
                user_id=user1.id,
                content='今天尝试了牛油果水波蛋吐司，第一次做水波蛋居然成功了！秘诀是水里加白醋，用勺子搅出漩涡再下蛋。早餐这样吃，一整天都元气满满。',
                image='https://lh3.googleusercontent.com/aida-public/AB6AXuBWCoRWf35e_dNWXLpeZWhsKHgeY-zVv6EnjN3c0eM1AtF7MMoxOmUVW8-l1TrlyxiJ6kIgMGlnoXb9LhqJphxsIRFMS4y2mm49SGlUhx1-8ocpAS1TPq9eaZ0qG6LSDTjkSApI7sABbITnQf4PCA5W1IxMklQvdoLN--JgjkouYb2KztGNCOg3tTO-p-Rh0HdzAvCn9OaeY7zX1tDDm72_YgsTVvlOqlUeTq_U1_cxgLAMZo68BYBYbUfSM483xHtlIWveDQpdMco7',
                category='recipe'
            ),
            CommunityPost(
                user_id=admin.id,
                content='晨跑 5 公里打卡！配速 6 分 30 秒，虽然不快但坚持下来了。跑完来一杯黑咖啡，帮助加速代谢。运动+轻食，效果翻倍。',
                image='',
                category='workout'
            ),
            CommunityPost(
                user_id=user1.id,
                content='发现一个超好用的控卡小技巧：用小一号的餐具吃饭，心理上觉得吃了很多，实际热量控制得很好。另外推荐希腊酸奶代替普通酸奶，蛋白质含量高一倍！',
                image='',
                category='share'
            ),
            CommunityPost(
                user_id=admin.id,
                content='专家提醒：减脂期间不要完全戒掉碳水化合物。优质碳水（糙米、燕麦、红薯）是身体的重要能量来源，完全断碳会导致代谢下降、肌肉流失。建议每日碳水占总热量的 30-40%。',
                image='',
                category='expert'
            ),
            CommunityPost(
                user_id=user1.id,
                content='周末 meal prep 打包完毕！提前准备好一周的午餐便当，再也不用纠结每天吃什么了。这次做了 5 种不同的沙拉搭配，每天换着吃不会腻。',
                image='https://lh3.googleusercontent.com/aida-public/AB6AXuCBryIQ5tZE6o2ofnuhWPvxu4hm-dZ3a_HCwxoyk40yKzizC7m6z_bby013e8905S1nW8gkIb4G4iN800sM1L2FtY1QqPwdaGd9u5a1y8MBp0gFFawuRyxjK6gFQ8NuaFBixNSDxpkH81e2NUOd5DFiCpEyDGpMh5EcK663YjBr0kw9vOey4MofsioB9TVKIKUV0B4WqWVwwoLGOBZMB7r_ttlGoq6jaCQIM2ma5GXC5GE4ShomIn8uKCk9tGYbOsqtOMSx_9Y5-zmd',
                category='share'
            ),
            CommunityPost(
                user_id=admin.id,
                content='三文鱼真的是减脂神器！富含 Omega-3 脂肪酸，既能抗炎又能促进脂肪代谢。今天晚餐是柠檬香煎三文鱼配芦笋，380 大卡，蛋白质 28g，吃完超满足。',
                image='https://lh3.googleusercontent.com/aida-public/AB6AXuD6UlzqXdAvKEfShYuVrgLEmA6aSxCuuWjQzOYdQQri6Hcg90TMy189kWAeLts5cUqPN286U__KXEpJTBr-l0ttIOpnncwIAr9npIxcMEyyzViGuHu_H3uo-a5HGUVE7sPRhgUqmdTSxZm0NkT3lCvKgm8gc02QsAhkc1pOjrg2TASErtHl4Az-m7r0KJuCipjLcXX2iAZT0YPMIJMX64NCep390-lkWjfFpcDjuqTBK4TtMfMSs95O4ejoFkPKLVpNKs5RqKoa5qvG',
                category='recipe'
            ),
            CommunityPost(
                user_id=user1.id,
                content='分享一下我的减脂心路历程：从 60kg 到 55kg，用了 3 个月。没有节食，就是合理控制热量+每周 3 次运动。最大的感悟是：减脂是一场马拉松，不是冲刺跑。慢慢来，比较快。',
                image='',
                category='share'
            ),
        ]
        db.session.add_all(posts)

        # 创建饮食记录（测试用户近 7 天）
        now = datetime.utcnow()
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        foods_list = Food.query.all()
        food_map = {f.name: f for f in foods_list}

        diet_records = []
        daily_data = [
            # (天数偏移, 早餐, 午餐, 晚餐, 加餐)
            (-6, '蓝莓坚果酸奶碗', '嫩煎鸡胸肉沙拉', '柠檬香煎三文鱼配芦笋', None),
            (-5, '牛油果水波蛋活力碗', '香煎鸡胸肉暖沙拉', None, '混合坚果与苹果片'),
            (-4, '蓝莓坚果酸奶碗', None, '柠檬香煎三文鱼配芦笋', '混合坚果与苹果片'),
            (-3, '牛油果水波蛋活力碗', '嫩煎鸡胸肉沙拉', '柠檬香煎三文鱼配芦笋', None),
            (-2, None, '香煎鸡胸肉暖沙拉', '柠檬香煎三文鱼配芦笋', '混合坚果与苹果片'),
            (-1, '蓝莓坚果酸奶碗', '嫩煎鸡胸肉沙拉', None, None),
            (0, '牛油果水波蛋活力碗', None, None, None),
        ]

        for day_offset, breakfast, lunch, dinner, snack in daily_data:
            day = today + timedelta(days=day_offset)
            meal_map = {'breakfast': breakfast, 'lunch': lunch, 'dinner': dinner, 'snack': snack}
            for meal_type, food_name in meal_map.items():
                if food_name and food_name in food_map:
                    food = food_map[food_name]
                    record = DietRecord(
                        user_id=user1.id,
                        food_id=food.id,
                        meal_type=meal_type,
                        calories=food.calories,
                        protein=food.protein,
                        amount=1,
                        recorded_at=day + timedelta(hours={'breakfast': 8, 'lunch': 12, 'dinner': 18, 'snack': 15}[meal_type])
                    )
                    diet_records.append(record)

        db.session.add_all(diet_records)

        # 创建饮水记录
        water_records = []
        for i in range(7):
            day = today + timedelta(days=i - 6)
            for cup in range(6):
                water_records.append(WaterRecord(
                    user_id=user1.id,
                    amount=250,
                    recorded_at=day + timedelta(hours=8 + cup * 2)
                ))
        db.session.add_all(water_records)

        # 创建运动类型库
        exercise_types = [
            # 有氧运动
            ExerciseType(name='跑步', category='cardio', met=8.0, icon='directions_run', description='户外或跑步机跑步'),
            ExerciseType(name='快走', category='cardio', met=4.5, icon='directions_walk', description='快速步行'),
            ExerciseType(name='骑行', category='cardio', met=7.0, icon='directions_bike', description='自行车骑行'),
            ExerciseType(name='游泳', category='cardio', met=7.0, icon='pool', description='自由泳/蛙泳等'),
            ExerciseType(name='跳绳', category='cardio', met=10.0, icon='fitness_center', description='跳绳运动'),
            ExerciseType(name='椭圆机', category='cardio', met=5.0, icon='fitness_center', description='椭圆机训练'),
            ExerciseType(name='划船机', category='cardio', met=6.0, icon='fitness_center', description='划船机训练'),
            # 力量训练
            ExerciseType(name='力量训练', category='strength', met=6.0, icon='fitness_center', description='器械/自由重量'),
            ExerciseType(name='俯卧撑', category='strength', met=5.0, icon='fitness_center', description='自重训练'),
            ExerciseType(name='深蹲', category='strength', met=5.0, icon='fitness_center', description='腿部力量训练'),
            ExerciseType(name='引体向上', category='strength', met=5.0, icon='fitness_center', description='背部力量训练'),
            ExerciseType(name='平板支撑', category='strength', met=4.0, icon='fitness_center', description='核心力量训练'),
            # 柔韧/平衡
            ExerciseType(name='瑜伽', category='flexibility', met=3.5, icon='self_improvement', description='瑜伽练习'),
            ExerciseType(name='拉伸', category='flexibility', met=2.5, icon='accessibility_new', description='全身拉伸'),
            ExerciseType(name='普拉提', category='flexibility', met=3.5, icon='self_improvement', description='普拉提训练'),
            # 运动
            ExerciseType(name='篮球', category='sports', met=7.0, icon='sports_basketball', description='篮球运动'),
            ExerciseType(name='足球', category='sports', met=8.0, icon='sports_soccer', description='足球运动'),
            ExerciseType(name='羽毛球', category='sports', met=5.5, icon='sports_tennis', description='羽毛球运动'),
            ExerciseType(name='乒乓球', category='sports', met=4.0, icon='sports_tennis', description='乒乓球运动'),
            ExerciseType(name='网球', category='sports', met=7.0, icon='sports_tennis', description='网球运动'),
            # 日常活动
            ExerciseType(name='爬楼梯', category='daily', met=5.0, icon='stairs', description='爬楼梯'),
            ExerciseType(name='家务', category='daily', met=3.0, icon='cleaning_services', description='做家务'),
            ExerciseType(name='散步', category='daily', met=2.5, icon='directions_walk', description='休闲散步'),
        ]
        db.session.add_all(exercise_types)

        db.session.commit()
        print('示例数据已填充')
        print('管理员账号: admin / admin123')
        print('测试账号: linyouxue / 123456')

        # 自动导入 HowToCook 食谱和图片
        print('\n正在导入 HowToCook 食谱...')
        try:
            from import_howtocook import import_recipes
            import_recipes()
        except Exception as e:
            print(f'导入 HowToCook 食谱失败: {e}')

        print('正在导入食谱图片...')
        try:
            from import_images import import_images
            import_images()
        except Exception as e:
            print(f'导入食谱图片失败: {e}')


if __name__ == '__main__':
    import sys
    force = '--force' in sys.argv
    init_database(force=force)
