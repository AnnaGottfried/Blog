from app import app, User,db,Items
import unittest

class FlaskTestCase(unittest.TestCase):


    def test_app(self):
        tester=app.test_client(self)
        response=tester.get('/login', content_type="html/text")
        self.assertEqual(response.status_code,200)

    # testuje /login

    def test_login_text(self):
        tester = app.test_client(self)
        response = tester.get('/login', content_type="html/text")
        self.assertTrue(b'Login' in response.data)

    def test_login_no_exist(self):
        tester = app.test_client(self)
        response = tester.post('/login', data=dict(username="admin", password="qwer"), follow_redirects=True)
        self.assertIn(b' U\xc5\xbcytkownik nie istnieje.Prosz\xc4\x99 si\xc4\x99 zarejestrowa\xc4\x87 ',response.data)

    def test_login_exist(self):
        tester = app.test_client(self)
        response = tester.post('/login', data=dict(username="AnnaGott", password="qaz"), follow_redirects=True)
        self.assertIn(b' Witaj AnnaGott', response.data)


if __name__ == '__main__':
   unittest.main()


'''
from flask_testing import TestCase
from flask_login import current_user

class BaseTestCase(TestCase):
    """A base test case."""

    def create_app(self):
        app.config.from_object('config.TestConfig')
        return app

    def setUp(self):
        db.create_all()
        db.session.add(User("Anna Gott", "gott@wp.pl", "AnnaGott", "qwe"))
        db.session.add(
            Item("Test post", "This is a test. Only a test.", "AnnaGott"))
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()'''