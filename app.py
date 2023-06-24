from flask import Flask, redirect, render_template, flash, g, session, request
from flask_debugtoolbar import DebugToolbarExtension
from models import *
from sqlalchemy.exc import IntegrityError
from forms import LoginForm, UserAddForm, MessageForm, EditUserForm

CURRENT_USER_KEY = 'current_user'

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///warbler_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_ECHO'] = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = 'dassa324'
debug = DebugToolbarExtension(app)

connect_db(app)

@app.before_request
def add_user_to_g():
    '''Before the requests it adds the current user to g'''
    if CURRENT_USER_KEY in session:
        g.user = User.query.get(session[CURRENT_USER_KEY])
    else:
        g.user = None

def do_login(user):
    '''Creates a session for the current user'''

    session[CURRENT_USER_KEY] = user.id

def do_logout():
    '''Logs user out and removes them from the session'''

    if CURRENT_USER_KEY in session:
        del session[CURRENT_USER_KEY]


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    '''Brings up signup form, makes new user. If username is taken it will flash message'''

    form = UserAddForm()

    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data
        try:
            new_user = User.register(
                username=username, 
                email=email, 
                password=password, 
                image_url=form.image_url.data or User.image_url.default.arg
            )

            db.session.add(new_user)
            db.session.commit()
            flash('Account Created!', 'success')
        except IntegrityError:
            flash('Username taken. Please Try Again', 'danger')
    
        do_login(new_user)

        return redirect('/')

    else:
        return render_template('users/signup.html', form=form)
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    '''Brings up login form'''

    form = LoginForm()

    if form.validate_on_submit():

        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)

        if user:
            do_login(user)
            flash(f'Welcome back, {user.username}!', 'success')
            return redirect('/')

        flash('Wrong username/password. Try again', 'danger')
        
    else:
        return render_template('users/login.html', form=form)
    
@app.route('/logout')
def logout():
    '''Logs user out'''
    do_logout()
    flash('Logged out', 'success')
    return redirect('/')

@app.route('/users')
def search_for_user():
    '''Makes a search for the user'''

    search = request.args.get('q')

    if not search:
        users = User.query.all()
    else:
        users = User.query.filter(User.username.like(f'%{search}%')).all()

    return render_template('/users/index.html', users=users)

@app.route('/users/<int:user_id>')
def show_user(user_id):
    '''Shows a list of the user and other messages'''

    user = User.query.get_or_404(user_id)

    messages = (Message
                .query
                .filter(Message.user_id == user_id)
                .order_by(Message.timestamp.desc())
                .limit(100)
                .all()
            )
    
    return render_template('users/show.html', user=user, messages=messages)

@app.route('/users/<int:user_id>/following')
def show_following(user_id):
    '''Shows who the user followed'''

    if not g.user:
        flash('You do no have access', 'danger')
        return redirect('/')

    user = User.query.get_or_404(user_id)
    return render_template('users/following.html', user=user)


@app.route('/users/<int:user_id>/followers')
def show_followers(user_id):
    '''Shows the user's followers'''

    if not g.user:
        flash('You do not have accces', 'danger')
        return redirect('/')
    user = User.query.get_or_404(user_id)

    return render_template('users/followers.html', user=user)


@app.route('/users/follow/<int:follow_id>', methods=['POST'])
def follow(follow_id):
    '''Shows the user who was just followed'''

    if not g.user:
        flash('You do not have access', 'danger')
        return redirect('/')
    
    followed_user = User.query.get_or_404(follow_id)
    try:
        g.user.following.append(followed_user)
        db.session.commit()
        flash(f'Following {followed_user.username}', 'success')
    except IntegrityError:
        flash("You can't follow yourself", 'danger')
        return redirect('/users')

    return redirect(f'/users/{g.user.id}/following')

@app.route('/users/stop-following/<int:follow_id>', methods=['POST'])
def stop_following(follow_id):
    '''Shows the user who was just unfollowed'''

    if not g.user:
        flash('You do not have access', 'danger')
        return redirect('/')
    
    followed_user = User.query.get_or_404(follow_id)
    g.user.following.remove(followed_user)
    db.session.commit()

    flash(f'Unfollowed {followed_user.username}', 'danger')

    return redirect(f'/users/{g.user.id}/following')

@app.route('/users/profile', methods=['GET', 'POST'])
def edit_profile():
    '''Shows profile edit form'''

    if not g.user:
        flash('You do no have access', 'danger')
        return redirect('/')

    form = EditUserForm()

    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data
        if User.authenticate(username=g.user.username, password=password):
            user = User.query.get_or_404(g.user.id)
            user.username = username
            user.email = email
            user.image_url = form.image_url.data or User.image_url.default.arg
            user.header_image_url = form.header_image_url.data or User.header_image_url.default.arg
            user.bio = form.bio.data
            user.location = form.location.data

            db.session.commit()
            flash('Changes saved!', 'success')
            return redirect(f'/users/{g.user.id}')
        
        else:
            flash('Changes were not made, incorrect password', 'danger')
            return redirect(f'/users/{g.user.id}')
    else:
            return render_template('/users/edit.html', form=form)

@app.route('/users/delete', methods=['POST'])
def delete_user():
    '''Deletes user from db'''

    if not g.user:
        flash('You do not have access', 'danger')
        return redirect('/')
    
    do_logout()
    
    db.session.delete(g.user)
    db.session.commit()
    flash('User deleted', 'success')

    return redirect('/signup')

@app.route('/messages/new', methods=['GET', 'POST'])
def new_message():
    '''Creates a new message'''

    if not g.user.id:
        flash('You do not have access', 'danger')
        return redirect('/')
    
    form = MessageForm()

    if form.validate_on_submit():
        text = form.text.data

        message = Message(text=text)
        g.user.messages.append(message)
        db.session.commit()

        return redirect(f'/users/{g.user.id}')
    
    else:
        return render_template('messages/new.html', form=form)
    
@app.route('/messages/<int:message_id>', methods=['GET'])
def show_specific_message(message_id):
    '''Shows messages by looking them by id'''
    message = Message.query.get_or_404(message_id)

    return render_template('messages/show.html', message=message)

@app.route('/messages/<int:message_id>/delete', methods=['POST'])
def delete_message(message_id):
    '''Deletes specific message'''

    if not g.user:
        flash('You do not have access', 'danger')
        return redirect('/')
    
    message = Message.query.get(message_id)

    db.session.delete(message)
    db.session.commit()

    return redirect(f'/users/{g.user.id}')

@app.route('/')
def homepage():
    '''If logged in, it will show a list of all posts. If a user is not logged in it will show the signup page'''

    if g.user:
        followed_users = [user.id for user in g.user.following]
        followed_users.append(g.user.id)
        user = User.query.get_or_404(g.user.id)
        messages = user.likes
        likes = [message.id for message in messages]
        messages = (Message
            .query
            .filter(Message.user_id.in_(followed_users))
            .order_by(Message.timestamp.desc())
            .limit(100)
            .all()
        )
        
        return render_template('home.html', messages=messages, user=user, likes=likes)
    else:
        return render_template('home-anon.html')
    
@app.route('/users/likes')
def show_liked_messages():
    '''Shows the user's likes'''
    if g.user:
        user = User.query.get_or_404(g.user.id)
        messages = user.likes
        likes = [message.id for message in messages]
        

        return render_template('users/likes.html', messages=messages, user=user, likes=likes)
    flash('You do not have access', 'danger')
    return redirect('/')
    
@app.route('/users/add_like/<int:message_id>', methods=['POST'])
def add_like(message_id):
    '''Gives ability to add and remove a like'''
    if g.user:
        user = g.user
        message = Message.query.get_or_404(message_id)
        if message.user_id != g.user.id:
            try:
                existing_like = Likes.query.filter_by(user_id=user.id, message_id=message_id).first()
                if existing_like:
                    db.session.delete(existing_like)
                    db.session.commit()
                    flash('Unliked', 'danger')
                else:
                    new_like = Likes(user_id=user.id, message_id=message.id)

                    db.session.add(new_like)
                    db.session.commit()
                    flash('Liked!', 'success')
                    return redirect('/')
            except IntegrityError:
                db.session.rollback()
                flash('Already liked', 'danger')
    return redirect('/')

    
@app.after_request
def add_header(req):

    req.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    req.headers['Pragma'] = 'no-cache'
    req.headers['Expires'] = '0'
    req.headers['Cache-Control'] = 'public, max-age=0'
    return req