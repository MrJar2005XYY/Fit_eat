from datetime import datetime
from models import db


class Notification(db.Model):
    """通知表"""
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    type = db.Column(db.String(20), default='')  # achievement/comment/like/system/reminder
    title = db.Column(db.String(100), default='')
    content = db.Column(db.Text, default='')
    link = db.Column(db.String(200), default='')  # 关联链接
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'type': self.type,
            'title': self.title,
            'content': self.content,
            'link': self.link,
            'isRead': self.is_read,
            'time': self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else '',
            'timeAgo': self._time_ago(),
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

    def __repr__(self):
        return f'<Notification {self.title}>'
