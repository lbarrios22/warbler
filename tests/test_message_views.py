from unittest import TestCase
from app import app, db
from models import User, Message

# Set up a test database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///warbler_db'
app.config['SQLALCHEMY_ECHO'] = False
app.config['TESTING'] = True
app.config['WTF_CSRF_ENABLED'] = False
app.config['SECRET_KEY'] = 'testsecretkey'
db.create_all()

class MessageViewsTestCase(TestCase):
    def setUp(self):
        """Set up the test environment"""
        db.drop_all()
        db.create_all()

        user = User(username='testuser', email='test@example.com', password='password')
        db.session.add(user)
        db.session.commit()

        self.user = user

        self.client = app.test_client()

    def tearDown(self):
        """Clean up the test environment"""
        db.session.rollback()
        db.drop_all()

    def test_add_message(self):
        """Test adding a new message"""
        with self.client as client:
            with client.session_transaction() as session:
                session['user_id'] = self.user.id

            response = client.post('/messages', data={'text': 'Test message'}, follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Test message', response.data)

    def test_delete_message(self):
        """Test deleting a message"""
        message = Message(text='Test message', user_id=self.user.id)
        db.session.add(message)
        db.session.commit()

        with self.client as client:
            with client.session_transaction() as session:
                session['user_id'] = self.user.id

            response = client.post(f'/messages/{message.id}/delete', follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertNotIn(b'Test message', response.data)

# Run the tests
if __name__ == '__main__':
    import unittest

    unittest.main()
