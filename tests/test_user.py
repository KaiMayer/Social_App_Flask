import unittest
from app.main.models import Permission
from app.users.models import User, AnonymousUser


class UserTestCase(unittest.TestCase):
    def test_password_setter(self):
        user = User(password='test')
        self.assertTrue(user.password_hash is not None)

    def test_password_is_not_readable(self):
        user = User(password='test')
        with self.assertRaises(AttributeError):
             user.password

    def test_correct_password(self):
        user = User(password='true')
        self.assertTrue(user.check_password('true'))
        self.assertFalse(user.check_password('false'))

    def test_user_role(self):
        user = User(email='test@example.com', password='test')

        self.assertTrue(user.check_access(Permission.FOLLOW))
        self.assertTrue(user.check_access(Permission.COMMENT))
        self.assertTrue(user.check_access(Permission.WRITE))
        self.assertFalse(user.check_access(Permission.ADMIN))

    def test_anonymous_user(self):
        user = AnonymousUser()

        self.assertFalse(user.check_access(Permission.FOLLOW))
        self.assertFalse(user.check_access(Permission.COMMENT))
        self.assertFalse(user.check_access(Permission.WRITE))
        self.assertFalse(user.check_access(Permission.ADMIN))
