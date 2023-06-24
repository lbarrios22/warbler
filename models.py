from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import datetime

db = SQLAlchemy()
bcrypt = Bcrypt()

def connect_db(app):
    db.app = app
    db.init_app(app)
    app.app_context().push()


class Follows(db.Model):
    ''' Represents the association table for tracking user following relationships.'''

    __tablename__ = 'follows'

    user_being_followed_id = db.Column(
        db.Integer, 
        db.ForeignKey('users.id', ondelete='CASCADE'),  
        primary_key=True
    )

    user_following_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
    )

class Likes(db.Model):
    '''Shows the likes using the user_id and the message_id'''

    __tablename__ = 'likes'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))

    message_id = db.Column(db.Integer, db.ForeignKey('messages.id', ondelete='CASCADE'), unique=True)


class User(db.Model):
    '''Makes a User class to add to db'''

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    email = db.Column(db.Text, nullable=False, unique=True)

    username = db.Column(db.Text, nullable=False, unique=True)

    image_url = db.Column(db.Text, default='/static/images/default-pic.png')

    header_image_url = db.Column(db.Text, default='/static/images/warbler-hero.jpg')

    bio = db.Column(db.Text)

    location = db.Column(db.Text)

    password = db.Column(db.Text, nullable=False)

    messages = db.relationship('Message')

    followers = db.relationship(
        'User', 
        secondary='follows', 
        primaryjoin=(Follows.user_following_id == id),
        secondaryjoin=(Follows.user_being_followed_id == id)
    )

    following = db.relationship(
        'User', 
        secondary='follows',
        primaryjoin=(Follows.user_following_id == id),
        secondaryjoin=(Follows.user_being_followed_id == id)
    )

    likes = db.relationship('Message', secondary='likes')

    def __repr__(self):
        return f'<User #{self.id}: {self.username}, {self.email}>'
    
    def is_followed_by(self, other_user):
        '''Checks to see if the user is getting followed'''
        found_user_list = [user for user in self.followers if user == other_user]
        return len(found_user_list) == 1
    
    def is_following(self, other_user):
        '''Checks to see if the user is following another user'''
        found_user_list = [user for user in self.followers if user == other_user]
        return len(found_user_list) == 1
    
    @classmethod
    def register(cls, username, email, password, image_url):
        '''Creates an encrypted password'''

        hashed_password = bcrypt.generate_password_hash(password)
        password_utf8 = hashed_password.decode('UTF-8')

        return cls(
            username=username,
            email=email,
            password=password_utf8,
            image_url=image_url
        )

    @classmethod
    def authenticate(cls, username, password):
        '''Authenticates password coming from an input'''

        user = cls.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, password):
            return user
        else:
            return False
    

class Message(db.Model):
    '''Creates message/post'''

    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    text = db.Column(db.String(50), nullable=False)

    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())

    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)

    user = db.relationship('User')