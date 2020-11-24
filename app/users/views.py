from flask import render_template, flash, redirect, \
    url_for, abort, request
from app import db
from .models import User
from app.main.models import Role, Post, Permission
from . import users
from .forms import EditUserProfileForm, EditUserAdminForm
from flask_login import login_required, current_user
from ..decorators import admin_required
from ..decorators import permission_required


@users.route('/user_profile/<username>')
def user_profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    if user is None:
        abort(404)
    posts = user.posts.order_by(Post.timestamp.desc()).all()
    return render_template('users/user_profile.html', user=user, posts=posts)


@users.route('/edit-user-profile', methods=['GET', 'POST'])
@login_required
def edit_user_profile():
    form = EditUserProfileForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = User.save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.name = form.name.data
        current_user.description = form.description.data
        db.session.add(current_user._get_current_object())
        db.session.commit()
        flash('Your profile has been successfully updated')
        return redirect(url_for('users.user_profile', username=current_user.username))
    form.name.data = current_user.name
    form.description.data = current_user.description
    return render_template('users/edit_user_profile.html', form=form)


@users.route('/edit-profile/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(user_id):
    user = User.query
    form = EditUserAdminForm(user=user)
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = user.save_picture(form.picture.data)
            user.image_file = picture_file
        user.email = form.email.data
        user.username = form.username.data3
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.description = form.description.data
        db.session.add(user)
        db.session.commit()
        flash('User profile has been successfully updated')
        return redirect(url_for('user_profile', username=current_user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.role.data = user.role_id
    form.name.data = user.name
    form.description = user.description
    return render_template('users/edit_user_profile.html', user=user, form=form)


@users.route('/follow/<username>')
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


@users.route('/unfollow/<username>')
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
@users.route('/followers/<username>')
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
    return render_template('users/followers.html', user=user, title="Followers of",
                           endpoint='.followers', pagination=pagination, follows=follows)


@users.route('/followed_by/<username>')
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
    return render_template('users/followers.html', user=user, title="Followed by",
                           endpoint='.followed_by', pagination=pagination,
                           follows=follows)

