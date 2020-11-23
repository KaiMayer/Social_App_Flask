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
    # initialize form
    form = PostForm()
    # if user has permission then set data from form to variable
    if current_user.check_access(Permission.WRITE) and form.validate_on_submit():
        # the author of the comment cannot be set directly to current_user because this is a context variable proxy
        # and current_user._get_current_object() returns the actual User object
        post = Post(content=form.content.data,
                    author=current_user._get_current_object())
        # if there is image then use custom save func to resize and save it
        if form.picture.data:
            picture_file = post.save_picture(form.picture.data)
            post.image_file = picture_file
        # save to db
        db.session.add(post)
        db.session.commit()
        # redirect to updated home page
        return redirect(url_for('main.index'))
    page = request.args.get('page', 1, type=int)
    # default not to show followed tab
    show_followed = False
    # if user is registered then show followed tab
    if current_user.is_authenticated:
        show_followed = bool(request.cookies.get('show_followed', ''))  # get value from cookie
    if show_followed:
        query = current_user.followed_posts  # custom query with with added followed posts
    else:
        query = Post.query  # default query
    # pagination to order posts items from query
    pagination = query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=5,
        error_out=False)
    posts = pagination.items  # set ordered posts
    outer_posts = True  # variable to check if to show 'see more' tab and not show all text in post
    return render_template('index.html', form=form, posts=posts,
                           show_followed=show_followed,
                           pagination=pagination,
                           outer_posts=outer_posts)


@main.route('/all')
@login_required
def show_all():
    resp = make_response(redirect(url_for('main.index')))
    # set cookie to show all posts
    resp.set_cookie('show_followed', '', max_age=30 * 24 * 60 * 60)  # 30 days
    return resp


@main.route('/followed')
@login_required
def show_followed():
    resp = make_response(redirect(url_for('main.index')))
    # set cookie to show followed posts
    resp.set_cookie('show_followed', '1', max_age=30 * 24 * 60 * 60)  # 30 days
    return resp


# edit post route
@main.route('/edit-post/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
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
    # load the user
    user = User.query.filter_by(username=username).first()
    # verify if it is valid
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('main.index'))
    # verify if it isn't already following
    if current_user.is_following(user):
        flash('You are already following this user.')
        return redirect(url_for('users.user_profile', username=username))
    # call helper function from follow model
    current_user.follow(user)
    db.session.commit()
    flash('You are now following %s.' % username)
    return redirect(url_for('users.user_profile', username=username))


@main.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
    # load the user
    user = User.query.filter_by(username=username).first()
    # verify if it is valid
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('main.index'))
    # verify if it is following
    if not current_user.is_following(user):
        flash('You are not following this user.')
        return redirect(url_for('users.user_profile', username=username))
    # call helper method from follow model
    current_user.unfollow(user)
    db.session.commit()
    flash('You are not following %s anymore.' % username)
    return redirect(url_for('users.user_profile', username=username))


# count followers
@main.route('/followers/<username>')
def followers(username):
    # load the user
    user = User.query.filter_by(username=username).first()
    # verify user
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('main.index'))
    page = request.args.get('page', 1, type=int)
    # paginate the list of followers
    pagination = user.followers.paginate(
        page, per_page=10,
        error_out=False)
    # Since the query for followers returns Follow instances,
    # the list is converted into another list that has user
    # and timestamp fields in each entry
    follows = [{'user': item.follower, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html', user=user, title="Followers of",
                           endpoint='.followers', pagination=pagination, follows=follows)


@main.route('/followed_by/<username>')
def followed_by(username):
    # get user
    user = User.query.filter_by(username=username).first()
    # verify if it is valid
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('main.index'))
    page = request.args.get('page', 1, type=int)
    # paginate the list of followed
    pagination = user.followed.paginate(
        page, per_page=10,
        error_out=False)
    # Since the query for followed returns Follow instances,
    # the list is converted into another list that has user
    # and timestamp fields in each entry
    follows = [{'user': item.followed, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html', user=user, title="Followed by",
                           endpoint='.followed_by', pagination=pagination,
                           follows=follows)


# also post comment route
@main.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
    post = Post.query.get_or_404(id)
    form = CommentForm()

    if form.validate_on_submit():
        # the author of the comment cannot be set directly to current_user because this is a context variable proxy
        # and current_user._get_current_object() returns the actual User object
        comment = Comment(body=form.body.data, post=post, author=current_user._get_current_object())
        db.session.add(comment)
        db.session.commit()
        flash('Your comment has been published.')
        return redirect(url_for('main.post', id=post.id, page=-1))

    page = request.args.get('page', 1, type=int)
    # -1 used to request the last page so that comment could appear
    if page == -1:
        # calculate the actual page number to use
        page = (post.comments.count() - 1) // 10 + 1  # 10: number of comments per page

    pagination = post.comments.order_by(Comment.timestamp.asc()).paginate(page, per_page=10, error_out=False)
    comments = pagination.items
    return render_template('post.html', posts=[post], form=form, comments=comments, pagination=pagination)


@main.route('/edit_comment/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_comment(id):
    form = CommentForm()
    comment = Comment.query.get_or_404(id)
    if current_user != comment.author and not current_user.check_access(Permission.ADMIN):
        abort(403)
    if form.validate_on_submit():
        comment.body = form.body.data
        db.session.add(comment)
        db.session.commit()
        flash('The comment has been updated.')
        return redirect(url_for('main.index', id=comment.id))
    form.body.data = comment.body
    return render_template('edit_comment.html', form=form)


@main.route('/like/<int:post_id>/<action>', methods=['GET', 'POST'])
@login_required
def like_action(post_id, action):
    # get post
    post = Post.query.filter_by(id=post_id).first_or_404()

    if action == 'like':
        # like helper method from user model
        current_user.like_post(post)
        db.session.commit()
    if action == 'unlike':
        # like helper method from user model
        current_user.unlike_post(post)
        db.session.commit()

    post.likes.count()
    return render_template('_likes.html', post=post)


# works only in testing mode
@main.route('/shutdown')
def server_shutdown():
    if not current_app.testing:
        # return error if not testing mode
        abort(404)
    shutdown = request.environ.get('werkzeug.server.shutdown')
    # verify shutdown command
    if not shutdown:
        abort(500)
    # exit server gracefully
    shutdown()
    return 'Shutting down...'

