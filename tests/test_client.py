import unittest
from app import create_app, db
from app.main.models import Role


class SocialAppClientTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()
        self.client = self.app.test_client(use_cookies=True)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_register_and_login(self):
        # register a new account
        response = self.client.post('/authentication/registration', data={
            'email': 'test@example.com',
            'username': 'username',
            'password': 'test',
            'confirm_password': 'test'
        })
        self.assertEqual(response.status_code, 200)

        # login with the new account
        response = self.client.post('/authentication/login', data={
            'email': 'test@example.com',
            'password': 'test'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        # log out
        response = self.client.get('/authentication/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
