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
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    comments = db.relationship('Comment', backref='post', lazy='dynamic', cascade='all, delete-orphan')
    likes = db.relationship('Like', backref='post', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self, current_user_id=None):
        is_liked = False
        if current_user_id:
            is_liked = Like.query.filter_by(post_id=self.id, user_id=current_user_id).first() is not None

        return {
            'id': self.id,
            'user': {
                'id': self.user_id,
                'name': self.user.username,
                'avatar': self.user.avatar,
            },
            'content': self.content,
            'image': self.image,
            'location': self.location,
            'category': self.category,
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

    def to_dict(self):
        return {
            'id': self.id,
            'postId': self.post_id,
            'user': {'id': self.user_id, 'name': self.user.username, 'avatar': self.user.avatar},
            'content': self.content,
            'time': self.created_at.strftime('%Y-%m-%d %H:%M'),
        }


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
