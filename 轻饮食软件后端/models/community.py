from datetime import datetime
from models import db


class CommunityPost(db.Model):
    __tablename__ = 'community_posts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    content = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(500), default='')
    location = db.Column(db.String(50), default='')
    category = db.Column(db.String(20), default='all')
    food_id = db.Column(db.Integer, db.ForeignKey('foods.id'), nullable=True)  # 关联食物
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    comments = db.relationship('Comment', backref='post', lazy='dynamic', cascade='all, delete-orphan')
    likes = db.relationship('Like', backref='post', lazy='dynamic', cascade='all, delete-orphan')
    food = db.relationship('Food', backref='community_posts')

    def to_dict(self, current_user_id=None):
        is_liked = False
        if current_user_id:
            is_liked = Like.query.filter_by(post_id=self.id, user_id=current_user_id).first() is not None

        food_info = None
        if self.food:
            food_info = {
                'id': self.food.id,
                'name': self.food.name,
                'image': self.food.image,
                'calories': self.food.calories,
            }

        return {
            'id': self.id,
            'user': {
                'id': self.user_id,
                'name': self.user.username if self.user else '已注销用户',
                'avatar': self.user.avatar if self.user else '',
            },
            'content': self.content,
            'image': self.image,
            'location': self.location,
            'category': self.category,
            'food': food_info,
            'likes': self.likes.count(),
            'comments': self.comments.count(),
            'isLiked': is_liked,
            'time': self._time_ago(),
        }

    def _time_ago(self):
        diff = datetime.utcnow() - self.created_at
        seconds = diff.total_seconds()
        if seconds < 60:
            return '刚刚'
        elif seconds < 3600:
            return f'{int(seconds // 60)}分钟前'
        elif seconds < 86400:
            return f'{int(seconds // 3600)}小时前'
        elif seconds < 604800:
            return f'{int(seconds // 86400)}天前'
        else:
            return self.created_at.strftime('%m月%d日')


class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('community_posts.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='comments')
    comment_likes = db.relationship('CommentLike', backref='comment', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self, current_user_id=None):
        is_liked = False
        if current_user_id:
            is_liked = CommentLike.query.filter_by(comment_id=self.id, user_id=current_user_id).first() is not None

        return {
            'id': self.id,
            'postId': self.post_id,
            'user': {
                'id': self.user_id,
                'name': self.user.username if self.user else '已注销用户',
                'avatar': self.user.avatar if self.user else ''
            },
            'content': self.content,
            'likes': self.comment_likes.count(),
            'isLiked': is_liked,
            'time': self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else '',
        }


class CommentLike(db.Model):
    """评论点赞表"""
    __tablename__ = 'comment_likes'

    id = db.Column(db.Integer, primary_key=True)
    comment_id = db.Column(db.Integer, db.ForeignKey('comments.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('comment_id', 'user_id'),)


class Like(db.Model):
    __tablename__ = 'likes'

    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('community_posts.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('post_id', 'user_id'),)


class Follow(db.Model):
    __tablename__ = 'follows'

    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    following_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('follower_id', 'following_id'),)


class Favorite(db.Model):
    __tablename__ = 'favorites'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    food_id = db.Column(db.Integer, db.ForeignKey('foods.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('user_id', 'food_id'),)
