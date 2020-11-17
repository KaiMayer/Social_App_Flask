from flask import render_template, redirect, request, url_for, \
    flash
from flask_login import login_user, logout_user, login_required
from . import authentication
from app.users.models import User
from .forms import LoginForm, RegisterForm
from app import db


@authentication.route('/registration', methods=['GET', 'POST'])
def registration():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(username=form.username.data,
                    email=form.email.data,
                    password=form.password.data,)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been successfully created')
        return redirect(url_for('authentication.login'))
    return render_template('authentication/registration.html', form=form)


@authentication.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.check_password(form.password.data):
            login_user(user, form.stay_logged_in.data)
            next = request.args.get('next')
            if next is None or not next.startswith('/'):
                next = url_for('main.index')
            return redirect(next)
        flash('Invalid email or password')
    return render_template('authentication/login.html', form=form)


@authentication.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You are logged out')
    return redirect(url_for('main.index'))

