from flask import Blueprint, request, jsonify, session
from models import db
from models.user import User
from models.community import CommunityPost, Comment, Like, Follow

community_bp = Blueprint('community', __name__)


def get_current_user():
    user_id = session.get('user_id')
    if not user_id:
        return None
    return User.query.get(user_id)


@community_bp.route('/posts', methods=['GET'])
def get_posts():
    user = get_current_user()
    page = request.args.get('page', 1, type=int)
    category = request.args.get('category', 'all')
    keyword = request.args.get('q', '').strip()

    query = CommunityPost.query
    if category and category != 'all':
        query = query.filter_by(category=category)

    # 搜索功能
    if keyword:
        query = query.filter(
            db.or_(
                CommunityPost.content.contains(keyword),
                CommunityPost.user.has(User.username.contains(keyword))
            )
        )

    posts = query.order_by(CommunityPost.created_at.desc()).paginate(
        page=page, per_page=10, error_out=False
    )

    user_id = user.id if user else None
    return jsonify([p.to_dict(current_user_id=user_id) for p in posts.items])


@community_bp.route('/posts', methods=['POST'])
def create_post():
    user = get_current_user()
    if not user:
        return jsonify({'success': False, 'message': '未登录'}), 401

    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': '请求数据无效'}), 400
    post = CommunityPost(
        user_id=user.id,
        content=data.get('content', ''),
        image=data.get('image', ''),
        location=data.get('location', ''),
        category=data.get('category', 'all'),
        food_id=data.get('foodId')
    )
    db.session.add(post)
    db.session.commit()

    # 检查成就解锁
    from routes.achievement import check_and_unlock_achievements
    check_and_unlock_achievements(user.id)

    return jsonify({'success': True, 'postId': post.id})


@community_bp.route('/posts/<int:post_id>/like', methods=['POST'])
def toggle_like(post_id):
    user = get_current_user()
    if not user:
        return jsonify({'success': False, 'message': '未登录'}), 401

    post = CommunityPost.query.get(post_id)
    if not post:
        return jsonify({'success': False, 'message': '动态不存在'}), 404

    existing = Like.query.filter_by(post_id=post_id, user_id=user.id).first()
    if existing:
        db.session.delete(existing)
        db.session.commit()
        return jsonify({'success': True, 'isLiked': False})
    else:
        like = Like(post_id=post_id, user_id=user.id)
        db.session.add(like)
        db.session.commit()
        return jsonify({'success': True, 'isLiked': True})


@community_bp.route('/posts/<int:post_id>/comment', methods=['POST'])
def add_comment(post_id):
    user = get_current_user()
    if not user:
        return jsonify({'success': False, 'message': '未登录'}), 401

    post = CommunityPost.query.get(post_id)
    if not post:
        return jsonify({'success': False, 'message': '动态不存在'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': '请求数据无效'}), 400
    content = data.get('content', '').strip()
    if not content:
        return jsonify({'success': False, 'message': '评论不能为空'}), 400

    comment = Comment(post_id=post_id, user_id=user.id, content=content)
    db.session.add(comment)
    db.session.commit()
    return jsonify({'success': True, 'commentId': comment.id})


@community_bp.route('/posts/<int:post_id>/comments', methods=['GET'])
def get_comments(post_id):
    user = get_current_user()
    user_id = user.id if user else None

    page = request.args.get('page', 1, type=int)
    comments = Comment.query.filter_by(post_id=post_id) \
        .order_by(Comment.created_at.desc()) \
        .paginate(page=page, per_page=20, error_out=False)

    return jsonify([c.to_dict(current_user_id=user_id) for c in comments.items])


@community_bp.route('/comments/<int:comment_id>/like', methods=['POST'])
def toggle_comment_like(comment_id):
    """评论点赞/取消点赞"""
    user = get_current_user()
    if not user:
        return jsonify({'success': False, 'message': '未登录'}), 401

    comment = Comment.query.get(comment_id)
    if not comment:
        return jsonify({'success': False, 'message': '评论不存在'}), 404

    from models.community import CommentLike
    existing = CommentLike.query.filter_by(comment_id=comment_id, user_id=user.id).first()
    if existing:
        db.session.delete(existing)
        db.session.commit()
        return jsonify({'success': True, 'isLiked': False})
    else:
        like = CommentLike(comment_id=comment_id, user_id=user.id)
        db.session.add(like)
        db.session.commit()
        return jsonify({'success': True, 'isLiked': True})


@community_bp.route('/my-posts', methods=['GET'])
def get_my_posts():
    user = get_current_user()
    if not user:
        return jsonify({'success': False, 'message': '未登录'}), 401

    page = request.args.get('page', 1, type=int)
    posts = CommunityPost.query.filter_by(user_id=user.id) \
        .order_by(CommunityPost.created_at.desc()) \
        .paginate(page=page, per_page=10, error_out=False)

    return jsonify([p.to_dict(current_user_id=user.id) for p in posts.items])


@community_bp.route('/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    user = get_current_user()
    if not user:
        return jsonify({'success': False, 'message': '未登录'}), 401

    post = CommunityPost.query.get(post_id)
    if not post:
        return jsonify({'success': False, 'message': '动态不存在'}), 404
    if post.user_id != user.id:
        return jsonify({'success': False, 'message': '无权删除'}), 403

    db.session.delete(post)
    db.session.commit()
    return jsonify({'success': True})


@community_bp.route('/follow/<int:user_id>', methods=['POST'])
def toggle_follow(user_id):
    user = get_current_user()
    if not user:
        return jsonify({'success': False, 'message': '未登录'}), 401

    target_user = User.query.get(user_id)
    if not target_user:
        return jsonify({'success': False, 'message': '用户不存在'}), 404

    if user.id == user_id:
        return jsonify({'success': False, 'message': '不能关注自己'}), 400

    existing = Follow.query.filter_by(follower_id=user.id, following_id=user_id).first()
    if existing:
        db.session.delete(existing)
        db.session.commit()
        return jsonify({'success': True, 'isFollowing': False})
    else:
        follow = Follow(follower_id=user.id, following_id=user_id)
        db.session.add(follow)
        db.session.commit()
        return jsonify({'success': True, 'isFollowing': True})
