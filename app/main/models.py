from app import db
from datetime import datetime
from flask import current_app, app
import os
import secrets
from PIL import Image


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    image_file = db.Column(db.String(28), default='default.jpg')
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    comments = db.relationship('Comment', backref='post', lazy='dynamic')
    likes = db.relationship('PostLike', backref='post', lazy='dynamic')

    @staticmethod
    def save_picture(form_picture):
        random_hex = secrets.token_hex(8)
        _, f_ext = os.path.splitext(form_picture.filename)
        picture_fn = random_hex + f_ext
        picture_path = os.path.join('app/static/post_pics', picture_fn)
        img = Image.open(form_picture)
        if img.height > 1280 or img.width > 1280:
            output_size = (1280, 720)
            img.thumbnail(output_size)
            img.save(picture_path)
        return picture_fn


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    disabled = db.Column(db.Boolean)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))


class PostLike(db.Model):
    __tablename__ = 'post_like'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))


class Follow(db.Model):
    __tablename__ = 'follows'
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                            primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                            primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class Permission:
    FOLLOW = 1
    COMMENT = 2
    WRITE = 4
    ADMIN = 8


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)

    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0

    def __repr__(self):
        return '<Role %r>' % self.name

    def has_permission(self, permission):
        return self.permissions & permission == permission

    def add_permission(self, permission):
        if not self.has_permission(permission):
            self.permissions += permission

    def remove_permissions(self, permission):
        self.permissions -= permission

    def reset_permissions(self):
        self.permissions = 0

    @staticmethod
    def insert_roles():
        roles = {
            'User': [Permission.FOLLOW, Permission.COMMENT, Permission.WRITE],
            'Moderator': [Permission.FOLLOW, Permission.COMMENT,
                          Permission.WRITE],
            'Administrator': [Permission.FOLLOW, Permission.COMMENT,
                              Permission.WRITE,
                              Permission.ADMIN],
        }
        default_role = 'User'
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.reset_permissions()
            for permission in roles[r]:
                role.add_permission(permission)
            role.default = (role.name == default_role)
            db.session.add(role)
        db.session.commit()



