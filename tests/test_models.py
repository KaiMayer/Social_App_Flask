import unittest
from datetime import datetime
from app import create_app, db
from app.main.models import Role, Permission
from app.users.models import Follow
from app.users.models import User, AnonymousUser


class UserModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_setter(self):
        user = User(password='test')
        self.assertTrue(user.password_hash is not None)

    def test_no_password_getter(self):
        user = User(password='test')
        with self.assertRaises(AttributeError):
            user.password

    def test_user_role(self):
        u = User(email='test@example.com', password='test')
        self.assertTrue(u.check_access(Permission.FOLLOW))
        self.assertTrue(u.check_access(Permission.COMMENT))
        self.assertTrue(u.check_access(Permission.WRITE))
        self.assertFalse(u.check_access(Permission.ADMIN))

    def test_administrator_role(self):
        r = Role.query.filter_by(name='Administrator').first()
        u = User(email='admin@example.com', password='admin', role=r)
        self.assertTrue(u.check_access(Permission.FOLLOW))
        self.assertTrue(u.check_access(Permission.COMMENT))
        self.assertTrue(u.check_access(Permission.WRITE))
        self.assertTrue(u.check_access(Permission.ADMIN))

    def test_anonymous_user(self):
        user = AnonymousUser()
        self.assertFalse(user.check_access(Permission.FOLLOW))
        self.assertFalse(user.check_access(Permission.COMMENT))
        self.assertFalse(user.check_access(Permission.WRITE))
        self.assertFalse(user.check_access(Permission.ADMIN))

    def test_timestamps(self):
        user = User(password='cat')
        db.session.add(user)
        db.session.commit()
        self.assertTrue(
            (datetime.utcnow() - user.created).total_seconds() < 3)

    def test_follows(self):
        u1 = User(email='user1@example.com', password='test')
        u2 = User(email='user2@example.org', password='test')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        self.assertFalse(u1.is_following(u2))
        self.assertFalse(u1.is_followed_by(u2))
        timestamp_before = datetime.utcnow()
        u1.follow(u2)
        db.session.add(u1)
        db.session.commit()
        timestamp_after = datetime.utcnow()
        self.assertTrue(u1.is_following(u2))
        self.assertFalse(u1.is_followed_by(u2))
        self.assertTrue(u2.is_followed_by(u1))
        self.assertTrue(u1.followed.count() == 1)
        self.assertTrue(u2.followers.count() == 1)
        f = u1.followed.all()[-1]
        self.assertTrue(f.followed == u2)
        self.assertTrue(timestamp_before <= f.timestamp <= timestamp_after)
        f = u2.followers.all()[-1]
        self.assertTrue(f.follower == u1)
        u1.unfollow(u2)
        db.session.add(u1)
        db.session.commit()
        self.assertTrue(u1.followed.count() == 0)
        self.assertTrue(u2.followers.count() == 0)
        self.assertTrue(Follow.query.count() == 0)
        u2.follow(u1)
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        db.session.delete(u2)
        db.session.commit()
        self.assertTrue(Follow.query.count() == 0)

