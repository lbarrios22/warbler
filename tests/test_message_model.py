from unittest import TestCase
from app import app, db
from models import User, Message

# Set up a test database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///warbler_db'
app.config['SQLALCHEMY_ECHO'] = False
app.config['TESTING'] = True
app.config['WTF_CSRF_ENABLED'] = False
db.create_all()

class MessageModelTestCase(TestCase):
    def setUp(self):
        """Set up the test environment"""
        db.drop_all()
        db.create_all()

        user = User(username='testuser', email='test@example.com', password='password')
        db.session.add(user)
        db.session.commit()

        self.user = user

    def tearDown(self):
        """Clean up the test environment"""
        db.session.rollback()
        db.drop_all()

    def test_message_creation(self):
        """Test message creation"""
        message = Message(text='Test message', user_id=self.user.id)
        db.session.add(message)
        db.session.commit()

        self.assertEqual(message.text, 'Test message')
        self.assertEqual(message.user_id, self.user.id)

# Run the tests
if __name__ == '__main__':
    import unittest

    unittest.main()
