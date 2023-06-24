from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, TextAreaField
from wtforms.validators import DataRequired, Email, Length

class MessageForm(FlaskForm):
    '''Makes a form to create a message/post'''

    text = TextAreaField('Message', validators=[DataRequired()])


class UserAddForm(FlaskForm):
    '''Create user form'''

    username = StringField('Username', validators=[DataRequired()])

    email = EmailField('Email', validators=[DataRequired()])

    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])

    image_url = StringField('Optional: Image URL')

class LoginForm(FlaskForm):
    '''Log in form'''

    username = StringField('Username', validators=[DataRequired()])

    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])

class EditUserForm(FlaskForm):
    '''This form is to edit the user'''

    username = StringField('Username', validators=[DataRequired()])

    email = EmailField('Email', validators=[DataRequired()])

    image_url = StringField('Optional: Image URL')

    header_image_url = StringField('Optional: Header Image URL')

    bio = TextAreaField('Optional: Bio')

    location = TextAreaField('Optional: Location(City, State)')

    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
