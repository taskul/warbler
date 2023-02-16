import os
from unittest import TestCase

from models import db, connect_db, Message, User, Likes, Follows
from bs4 import BeautifulSoup

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False

class UserViewsTestCase(TestCase):
    '''Testing User views'''
    
    def setUp(self):
        db.drop_all()
        db.create_all()

        self.client = app.test_client()

        self.u1 = User.signup(
            email='cat@cat.com', 
            username='cat',
            password='HelloWorld',
            image_url=None
        )
        self.u1.id = 1717
        self.u2 = User.signup(
            email='dog@dog.com', 
            username='dog',
            password='BuyMeBacon',
            image_url=None
        )
        self.u2.id = 1818

        db.session.commit()

    def tearDown(self):
        resp = super().tearDown()
        db.session.rollback()
        return resp

    def test_view_all_users(self):
        '''view all users'''
        with self.client as c:
            resp = c.get('/users')

            self.assertIn('@cat', str(resp.data))
            self.assertIn('@dog', str(resp.data))
            self.assertNotIn('@bird', str(resp.data))

    def test_get_user_profile(self):
        '''view user profile based on user id'''
        with self.client as c:
            resp = c.get(f'/users/{self.u1.id}')

            self.assertEqual(resp.status_code, 200)
            self.assertIn('cat', str(resp.data))

    def setup_likes(self):
        m1 = Message(text='Tuna is better than chicken', user_id=self.u1.id)
        m2 = Message(text='Bacon is a great treat', user_id=self.u2.id)
        m3 = Message(text='Why do people think that cats like milk?', user_id=self.u1.id)
        m1.id = 2020
        m2.id = 2021
        m3.id = 2023
        db.session.add_all([m1, m2, m3])
        db.session.commit()

        l1 = Likes(user_id = self.u2.id, message_id=m3.id)
        db.session.add(l1)
        db.session.commit()

    def test_likes(self):
        '''testing likes'''
        self.setup_likes()

        with self.client as c:
            resp = c.get(f'/users/{self.u2.id}')

            self.assertEqual(resp.status_code, 200)

            soup = BeautifulSoup(str(resp.data), 'html.parser')
            found = soup.find_all('li', {'class':'stat'})
            self.assertEqual(len(found), 4)

            # testing the number of messages by a u2
            self.assertIn('1', found[0].text)

    def test_add_like(self):
        '''testing adding likes'''
        m = Message(id=2023, text='Woof Woof', user_id=self.u2.id)
        db.session.add(m)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as user_session:
                user_session[CURR_USER_KEY] = self.u1.id

                resp = c.post(f'/users/add_like/{2023}', follow_redirects=True)
                self.assertEqual(resp.status_code, 200)

                likes = Likes.query.filter(Likes.message_id==2023).all()
                self.assertEqual(likes, 1)
                self.assertEqual(likes[0].user_id, self.u1.id)

    def test_remove_like(self):
        self.setup_likes()
         # u2 message id is 2021
        m = Message.query.get(2021)
        likes = Likes.query.filter(Likes.message_id==m.id).all()
        self.assertEqual(likes, [])
        







    
