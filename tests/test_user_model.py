import unittest
from app import app, db, User

# Define a test class for the User model
class UserModelTestCase(unittest.TestCase):
    
    def setUp(self):
        # Configure the app for testing
        app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///warbler_db'
        app.config['TESTING'] = True
        self.app = app.test_client()
        
        # Create the database and tables
        db.create_all()
        
    def tearDown(self):
        # Remove the database and tables
        db.drop_all()
    
    def test_repr_method(self):
        # Create a test user
        user = User(username='testuser', email='test@example.com', password='password')
        
        # Check if the repr method returns the expected representation
        self.assertEqual(repr(user), "<User #1: testuser, test@example.com>")
    
    def test_register_method(self):
        # Register a new user
        user = User.register('testuser', 'test@example.com', 'password', 'image_url')
        
        # Check if the user is created with the correct attributes
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.password.startswith('$2b$'))
    
    def test_authenticate_method(self):
        # Register a new user
        User.register('testuser', 'test@example.com', 'password', 'image_url')
        
        # Authenticate the user
        authenticated_user = User.authenticate('testuser', 'password')
        
        # Check if the user is authenticated successfully
        self.assertTrue(authenticated_user)
        self.assertEqual(authenticated_user.username, 'testuser')
        self.assertEqual(authenticated_user.email, 'test@example.com')
        
        # Try to authenticate with an invalid password
        invalid_password_user = User.authenticate('testuser', 'wrongpassword')
        
        # Check if the user is not authenticated with the invalid password
        self.assertFalse(invalid_password_user)
    
    # Add more test methods for other model attributes and methods

if __name__ == '__main__':
    unittest.main()
