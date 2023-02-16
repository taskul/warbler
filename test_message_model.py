import os
from unittest import TestCase
from sqlalchemy import exc
from models import db, User, Message, Follows
import datetime

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

class MessageModelTestCase(TestCase):
    '''Test views for messages'''

    def setUp(self):
        """Create test client, add sample data."""
        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

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

    def test_create_message(self):
        '''Testing creation of a message'''
        message = Message(text='Hello World', user_id=self.u1.id)
        db.session.add(message)
        db.session.commit()

        self.assertEqual(len(self.u1.messages), 1)
        self.assertEqual(self.u1.messages[0].text, 'Hello World')
        self.assertEqual(message.timestamp.year, 2023)