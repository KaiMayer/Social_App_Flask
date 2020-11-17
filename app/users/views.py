from flask import render_template, flash, redirect, \
    url_for, abort
from app import db
from .models import User
from app.main.models import Role, Post
from . import users
from .forms import EditUserProfileForm, EditUserAdminForm
from flask_login import login_required, current_user
from ..decorators import admin_required


@users.route('/user_profile/<username>')
def user_profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    if user is None:
        abort(404)
    posts = user.posts.order_by(Post.timestamp.desc()).all()
    return render_template('user_profile.html', user=user, posts=posts)


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
    return render_template('edit_user_profile.html', form=form)


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
    return render_template('edit_user_profile.html', user=user, form=form)
