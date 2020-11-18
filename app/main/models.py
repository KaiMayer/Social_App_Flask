from app import db
from datetime import datetime
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

    # set size and where the file(picture) is saved
    @staticmethod
    def save_picture(form_picture):
        random_hex = secrets.token_hex(8)  # generate token
        _, f_ext = os.path.splitext(form_picture.filename)  # get file extension
        picture_fn = random_hex + f_ext  # combine toke and file ext
        picture_path = os.path.join('app/static/post_pics', picture_fn)  # get the path and append where to save file
        img = Image.open(form_picture)
        # check the whether the img has large size
        if img.height > 1280 or img.width > 1280:
            output_size = (1280, 720)
            img.thumbnail(output_size)  # resize
            # save img
            img.save(picture_path)
        return picture_fn


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
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


# Used powers of two for permission values is that it allows permissions
# to be combined, giving each possible combination of permissions a unique value to
# store in the role’s permissions field
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
    default = db.Column(db.Boolean, default=False, index=True)  # set true for only one role and false to others
    permissions = db.Column(db.Integer)

    # To avoid None field by default, set it to 0 if an initial
    # value isn’t provided
    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0

    def __repr__(self):
        return '<Role %r>' % self.name

    # has_permission uses bitwise AND (&)
    # to check if a combined permission value has given permission.
    def has_permission(self, permission):
        return self.permissions & permission == permission

    def add_permission(self, permission):
        if not self.has_permission(permission):
            self.permissions += permission

    def remove_permissions(self, permission):
        self.permissions -= permission

    def reset_permissions(self):
        self.permissions = 0  # set no permissions

    # method to create(recreate) roles in db\server
    @staticmethod
    def insert_roles():
        # dictionary of roles
        roles = {
            'User': [Permission.FOLLOW, Permission.COMMENT, Permission.WRITE],
            'Moderator': [Permission.FOLLOW, Permission.COMMENT,
                          Permission.WRITE],
            'Administrator': [Permission.FOLLOW, Permission.COMMENT,
                              Permission.WRITE,
                              Permission.ADMIN],
        }
        # default role
        default_role = 'User'

        for r in roles:
            # get user role
            role = Role.query.filter_by(name=r).first()
            # assign role if no role set
            if role is None:
                role = Role(name=r)
            # reset permissions if there were some
            role.reset_permissions()
            # set new permissions
            for permission in roles[r]:
                role.add_permission(permission)
            role.default = (role.name == default_role)
            db.session.add(role)
        db.session.commit()



