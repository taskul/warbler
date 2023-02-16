"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from sqlalchemy import exc
from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for user actions."""

    def setUp(self):
        """Create test client, add sample data."""

        db.session.query(User).delete()
        Message.query.delete()
        Follows.query.delete()
        db.session.commit()

        u1 = User.signup(
            email='cat@cat.com', 
            username='cat',
            password='HelloWorld',
            image_url=None
        )
        u2 = User.signup(
            email='dog@dog.com', 
            username='dog',
            password='BuyMeBacon',
            image_url=None
        )
        db.session.commit()

        self.u1 = u1
        self.u2 = u2
        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)

    def test_user_model_repr(self):
        '''test __repr__'''
        u = User(
            email='cat@cat.com', 
            username='cat',
            password=123456
        )

        self.assertEqual(str(u), '<User #None: cat, cat@cat.com>')

    def test_user_model_following(self):
        '''Does is_following successfully detect when user1 is following user2?'''
        following = Follows(
            user_being_followed_id=self.u2.id, 
            user_following_id=self.u1.id
            )
        db.session.add(following)
        db.session.commit()

        self.assertEqual(self.u1.following[0].id, self.u2.id)

    def test_user_model_not_following(self):
        '''Does is_following successfully detect when user1 is not following user2?'''

        self.assertEqual(len(self.u1.following), 0)

    def test_user_model_followed(self):
        '''Does is_followed_by successfully detect when user1 is followed by user2?'''
        following = Follows(
            user_being_followed_id=self.u1.id,
            user_following_id=self.u2.id
            )
        db.session.add(following)
        db.session.commit()
        
        self.assertEqual(len(self.u1.followers), 1)
        self.assertEqual(self.u1.followers[0].id, self.u2.id)

    def test_user_model_not_followed(self):
        """Does is_followed_by successfully detect when user1 is not followed by user2?"""
        self.assertEqual(len(self.u1.followers), 0)

    def test_user_model_signup(self):
        """Does User.create successfully create a new user given valid credentials?"""
        u3 = User.signup(
            username='bird', 
            email='bird@birds.com',
            password='TweetTweet',
            image_url=None
        )

        # we have User #None because we haven't comitted this which means there is no ID
        self.assertEqual(str(u3), "<User #None: bird, bird@birds.com>")
        self.assertTrue(u3.password.startswith("$2b$"))

    def test_user_model_signup_fail(self):
        """Does User.create successfully create a new user given valid credentials?"""
        u3 = User.signup(
            username='cat', 
            email='cat@cat.com',
            password='TweetTweet',
            image_url=None
        )

        # Catching errors
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_user_model_authenticate(self):
        """Does User.authenticate successfully return a user when given a valid username and password?"""
        user = User.authenticate(self.u1.username, 'HelloWorld')

        self.assertEqual(user.username, 'cat')

    def test_user_model_authenticate_username_fail(self):
        """Does User.authenticate fail to return a user when the username is invalid?"""
        user = User.authenticate(self.u2.username, 'HelloWorld')

        self.assertEqual(user, False)

    def test_user_model_authenticate_password_fail(self):
        """Does User.authenticate fail to return a user when the username is invalid?"""
        user = User.authenticate(self.u1.username, 'CatsAreGreat')

        self.assertEqual(user, False)
