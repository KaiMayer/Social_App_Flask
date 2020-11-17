from app import db
from app import login_manager
from app.main.models import Post, Role, Permission, Follow, PostLike
from flask_login import UserMixin, AnonymousUserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.sql import func
from flask import current_app
import os
import secrets
from PIL import Image


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True, )
    name = db.Column(db.String(64))
    email = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    description = db.Column(db.Text(256))
    image_file = db.Column(db.String(28), default='default.jpg')
    created = db.Column(db.DateTime(timezone=True), default=func.now())
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    followed = db.relationship('Follow',
                               foreign_keys=[Follow.follower_id],
                               backref=db.backref('follower', lazy='joined'),
                               lazy='dynamic',
                               cascade='all, delete-orphan')
    followers = db.relationship('Follow',
                                foreign_keys=[Follow.followed_id],
                                backref=db.backref('followed', lazy='joined'),
                                lazy='dynamic',
                                cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='author', lazy='dynamic')
    liked = db.relationship('PostLike', foreign_keys='PostLike.user_id', backref='user', lazy='dynamic')

    def like_post(self, post):
        if not self.has_liked_post(post):
            like = PostLike(user_id=self.id, post_id=post.id)
            db.session.add(like)

    def unlike_post(self, post):
        if self.has_liked_post(post):
            PostLike.query.filter_by(
                user_id=self.id,
                post_id=post.id).delete()

    def has_liked_post(self, post):
        return PostLike.query.filter(
            PostLike.user_id == self.id,
            PostLike.post_id == post.id).count() > 0

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['SOCIAL_APP_ADMIN']:
                self.role = Role.query.filter_by(name='Administrator').first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()

    @staticmethod
    def save_picture(form_picture):
        random_hex = secrets.token_hex(8)
        _, f_ext = os.path.splitext(form_picture.filename)
        picture_fn = random_hex + f_ext
        picture_path = os.path.join(current_app.root_path, 'static/profile_pics', picture_fn)

        output_size = (125, 125)
        i = Image.open(form_picture)
        i.thumbnail(output_size)
        i.save(picture_path)

        return picture_fn

    @property
    def followed_posts(self):
        return Post.query.join(Follow, Follow.followed_id == Post.author_id) \
            .filter(Follow.follower_id == self.id)

    @property
    def password(self):
        raise AttributeError('Password is not available for reading')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def check_access(self, permission):
        return self.role is not None and self.role.has_permission(permission)

    def is_administrator(self):
        return self.check_access(Permission.ADMIN)

    def __repr__(self):
        return '<User %r>' % self.username

    def follow(self, user):
        if not self.is_following(user):
            f = Follow(follower=self, followed=user)
            db.session.add(f)

    def unfollow(self, user):
        f = self.followed.filter_by(followed_id=user.id).first()
        if f:
            db.session.delete(f)

    def is_following(self, user):
        if user.id is None:
            return False
        return self.followed.filter_by(
            followed_id=user.id).first() is not None

    def is_followed_by(self, user):
        if user.id is None:
            return False
        return self.followers.filter_by(
            follower_id=user.id).first() is not None


class AnonymousUser(AnonymousUserMixin):

    def check_access(self, permission):
        return False

    def is_administrator(self):
        return False

    def has_liked_post(self, post):
        return False


login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

