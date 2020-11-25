from flask import g, jsonify
from flask_httpauth import HTTPBasicAuth
from .errors import unauthorized, forbidden
from app.users.models import User
from . import api

auth = HTTPBasicAuth()


@auth.error_handler
def auth_error():
    return unauthorized('Invalid credentials')


@auth.verify_password
def check_password(email_or_token, password):
    if email_or_token == '':
        return False
    if password == '':
        g.current_user = User.verify_auth_token(email_or_token)
        g.token_used = True
        return g.current_user is not None
    user = User.query.filter_by(email=email_or_token).first()
    if not user:
        return False
    g.current_user = user
    g.token_used = False
    return user.check_password(password)


@api.route('/tokens/', methods=['POST'])
def get_token():
    if g.current_user.is_anonymous or g.token_used:
        return unauthorized('Invalid credentials')
    return jsonify({
        'token': g.current_user.generate_auth_token(expiration=3600),
        'expiration': 3600})


@api.before_request
@auth.login_required
def before_request():
    if g.current_user.is_anonymous:
        return forbidden('User is anonymous')
