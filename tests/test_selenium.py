import threading
import time
import unittest
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from app import create_app, db, fake_data
from app.main.models import Role, Post
from app.users.models import User


MAX_WAIT = 5


class SeleniumTestCase(unittest.TestCase):
    client = None

    def wait_for(self, fn):
        start_time = time.time()
        while True:
            try:
                time.sleep(0.5)
                return fn()
            except (AssertionError, WebDriverException) as e:
                if time.time() - start_time > MAX_WAIT:
                    raise e
                time.sleep(1)

    @classmethod
    def setUpClass(cls):
        # start Chrome
        options = webdriver.ChromeOptions()
        # options.add_argument('headless')
        try:
            cls.client = webdriver.Chrome(chrome_options=options)
        except:
            pass

        # skip these tests if the browser could not be started
        if cls.client:
            # create the application
            cls.app = create_app('testing')
            cls.app_context = cls.app.app_context()
            cls.app_context.push()

            # suppress logging to keep unittest output clean
            import logging
            logger = logging.getLogger('werkzeug')
            logger.setLevel("ERROR")

            # create the database and populate with some fake data
            db.create_all()
            Role.insert_roles()
            fake_data.users(5)
            fake_data.posts(5)

            # add an administrator user
            admin_role = Role.query.filter_by(name='Administrator').first()
            admin = User(email='test_admin@example.com',
                         username='test_admin', password='admin',
                         role=admin_role)
            db.session.add(admin)
            db.session.commit()

            # start the Flask server in a thread
            cls.server_thread = threading.Thread(target=cls.app.run,
                                                 kwargs={'debug': False})
            cls.server_thread.start()

            # give the server a second to ensure it is up
            time.sleep(1)

    @classmethod
    def tearDownClass(cls):
        if cls.client:
            # stop the flask server and the browser
            cls.client.get('http://localhost:5000/shutdown')
            cls.client.quit()
            cls.server_thread.join()

            # destroy database
            db.drop_all()
            db.session.remove()

            # remove application context
            cls.app_context.pop()

    def setUp(self):
        if not self.client:
            self.skipTest('Web browser not available')

    def tearDown(self):
        pass

    # work in progress :)
    # @unittest.skip
    def test_admin_home_page_and_make_post(self):
        # navigate to home page
        self.client.get('http://localhost:5000/')

        # navigate to login page
        self.wait_for(lambda: self.client.find_element_by_link_text('Log In').click())
        self.wait_for(lambda: self.assertIn('<h1>Login</h1>', self.client.page_source))

        # login
        self.wait_for(lambda: self.client.find_element_by_name('email').send_keys('test_admin@example.com'))
        self.wait_for(lambda: self.client.find_element_by_name('password').send_keys('admin'))
        self.wait_for(lambda: self.client.find_element_by_name('submit').click())
        self.wait_for(lambda:
                      self.assertIn('<h2>Hello, test_admin</h2>',
                                    self.client.page_source))
        # navigate to the user's profile page
        self.wait_for(lambda: self.client.find_element_by_link_text('Profile').click())
        self.wait_for(lambda: self.assertIn('<h1>test_admin</h1>', self.client.page_source))

        self.wait_for(lambda: self.client.find_element_by_link_text('Home').click())
        self.wait_for(lambda: self.client.find_element_by_css_selector('textarea').send_keys('Test post text comes here'))
        self.wait_for(lambda: self.client.find_element_by_id('submit').click())
        time.sleep(20)





