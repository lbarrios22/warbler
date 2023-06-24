import unittest
from app import app, db, User

class UserViewsTestCase(unittest.TestCase):
    
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
    
    def test_register_route(self):
        # Send a POST request to the register route with valid data
        response = self.app.post('/register', data=dict(
            username='testuser',
            email='test@example.com',
            password='password',
            image_url='image_url'
        ), follow_redirects=True)
        
        # Check if the user is redirected to the homepage after successful registration
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.path, '/')
        
        # Check if the user is created in the database
        user = User.query.filter_by(username='testuser').first()
        self.assertIsNotNone(user)
    
    def test_login_route(self):
        # Create a test user
        User.register('testuser', 'test@example.com', 'password', 'image_url')
        
        # Send a POST request to the login route with valid credentials
        response = self.app.post('/login', data=dict(
            username='testuser',
            password='password'
        ), follow_redirects=True)
        
        # Check if the user is redirected to the homepage after successful login
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.path, '/')
        
        # Check if the user is logged in
        with self.app as client:
            response = client.get('/profile')
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Profile Page', response.data)
    
    # Add more test methods for other user routes/view-functions

if __name__ == '__main__':
    unittest.main()
