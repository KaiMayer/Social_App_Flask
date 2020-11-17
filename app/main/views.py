from flask import render_template, flash, redirect, \
    url_for, current_app, abort, request, make_response
from app import db
from app.main.models import Post, Permission, Comment
from app.users.models import User
from . import main
from .forms import PostForm, CommentForm
from flask_login import login_required, current_user
from ..decorators import permission_required


@main.route('/', methods=['GET', 'POST'])
def index():
    form = PostForm()
    if current_user.check_access(Permission.WRITE) and form.validate_on_submit():
        post = Post(content=form.content.data,
                    author=current_user._get_current_object())
        if form.picture.data:
            picture_file = post.save_picture(form.picture.data)
            post.image_file = picture_file
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('main.index'))
    page = request.args.get('page', 1, type=int)
    show_followed = False
    if current_user.is_authenticated:
        show_followed = bool(request.cookies.get('show_followed', ''))
    if show_followed:
        query = current_user.followed_posts
    else:
        query = Post.query
    pagination = query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=5,
        error_out=False)
    posts = pagination.items
    outer_posts = True
    return render_template('index.html', form=form, posts=posts,
                           show_followed=show_followed,
                           pagination=pagination,
                           outer_posts=outer_posts)


@main.route('/all')
@login_required
def show_all():
    resp = make_response(redirect(url_for('main.index')))
    resp.set_cookie('show_followed', '', max_age=30 * 24 * 60 * 60)  # 30 days
    return resp


@main.route('/followed')
@login_required
def show_followed():
    resp = make_response(redirect(url_for('main.index')))
    resp.set_cookie('show_followed', '1', max_age=30 * 24 * 60 * 60)  # 30 days
    return resp


@main.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    form = PostForm()
    post = Post.query.get_or_404(id)
    if current_user != post.author and not current_user.check_access(Permission.ADMIN):
        abort(403)
    if form.validate_on_submit():
        post.content = form.content.data
        if form.picture.data:
            picture_file = post.save_picture(form.picture.data)
            post.image_file = picture_file
        db.session.add(post)
        db.session.commit()
        flash('The post has been updated.')
        return redirect(url_for('main.index', id=post.id))
    form.content.data = post.content
    form.picture.data = post.image_file
    return render_template('edit_post.html', form=form)


@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('main.index'))
    if current_user.is_following(user):
        flash('You are already following this user.')
        return redirect(url_for('users.user_profile', username=username))
    current_user.follow(user)
    db.session.commit()
    flash('You are now following %s.' % username)
    return redirect(url_for('users.user_profile', username=username))


@main.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('main.index'))
    if not current_user.is_following(user):
        flash('You are not following this user.')
        return redirect(url_for('users.user_profile', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash('You are not following %s anymore.' % username)
    return redirect(url_for('users.user_profile', username=username))


@main.route('/followers/<username>')
def followers(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('main.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followers.paginate(
        page, per_page=10,
        error_out=False)
    follows = [{'user': item.follower, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html', user=user, title="Followers of",
                           endpoint='.followers', pagination=pagination, follows=follows)


@main.route('/followed_by/<username>')
def followed_by(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('main.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followed.paginate(
        page, per_page=10,
        error_out=False)
    follows = [{'user': item.followed, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html', user=user, title="Followed by",
                           endpoint='.followed_by', pagination=pagination,
                           follows=follows)


@main.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
    post = Post.query.get_or_404(id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(body=form.body.data, post=post, author=current_user._get_current_object())
        db.session.add(comment)
        db.session.commit()
        flash('Your comment has been published.')
        return redirect(url_for('main.post', id=post.id, page=-1))
    page = request.args.get('page', 1, type=int)
    if page == -1:
        page = (post.comments.count() - 1) // 10 + 1
    pagination = post.comments.order_by(Comment.timestamp.asc()).paginate(page, per_page=10, error_out=False)
    comments = pagination.items
    return render_template('post.html', posts=[post], form=form, comments=comments, pagination=pagination)


@main.route('/like/<int:post_id>/<action>', methods=['GET', 'POST'])
@login_required
def like_action(post_id, action):
    post = Post.query.filter_by(id=post_id).first_or_404()

    if action == 'like':
        current_user.like_post(post)
        db.session.commit()
    if action == 'unlike':
        current_user.unlike_post(post)
        db.session.commit()

    post.likes.count()
    return render_template('_likes.html', post=post)


@main.route('/shutdown')
def server_shutdown():
    if not current_app.testing:
        abort(404)
    shutdown = request.environ.get('werkzeug.server.shutdown')
    if not shutdown:
        abort(500)
    shutdown()
    return 'Shutting down...'

