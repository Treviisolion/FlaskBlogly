"""Blogly application."""

from flask_debugtoolbar import DebugToolbarExtension
from flask import Flask, redirect, render_template, request, send_file
from models import db, connect_db, User

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

connect_db(app)

app.config['SECRET_KEY'] = 'JohnathonAppleseed452'
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
debug = DebugToolbarExtension(app)


@app.route('/')
def redirect_to_users():
    """Main page is /users redirect to there"""

    return redirect('/users')


@app.route('/static/uploads/default_user.png')
def return_default_user():
    """Returns the default user profile"""

    return send_file('static/uploads/default_user.png')


@app.route('/users')
def show_users():
    """Show all users"""

    users = User.query.all()
    return render_template('users.html', users=users)


@app.route('/users/<userid>')
def show_user(userid):
    """Show a specific user"""

    user = User.query.get_or_404(userid)
    return render_template('user.html', user=user)


@app.route('/users/new', methods=['GET'])
def show_new_user_form():
    """Show the form for creating a new user"""

    return render_template('new_user.html')


@app.route('/users/new', methods=['POST'])
def create_user():
    """Creates a user"""

    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    image_url = request.form.get('image_url', None)

    if not image_url:
        new_user = User(first_name=first_name, last_name=last_name)
    else:
        new_user = User(first_name=first_name,
                        last_name=last_name, image_url=image_url)
    db.session.add(new_user)
    db.session.commit()

    return redirect(f'/users')


@app.route('/users/<userid>/edit', methods=['GET'])
def show_edit_user_form(userid):
    """Returns the form for editing the specified user"""

    user = User.query.get_or_404(userid)
    return render_template('user_edit.html', user=user)


@app.route('/users/<userid>/edit', methods=['POST'])
def edit_user(userid):
    """Edit user in database"""

    user = User.query.get_or_404(userid)
    first_name = request.form.get('first_name', None)
    last_name = request.form.get('last_name', None)
    image_url = request.form.get('image_url', None)

    user.update_user(first_name, last_name, image_url)
    db.session.commit()

    return redirect('/users')


@app.route('/users/<userid>/delete', methods=['POST'])
def delete_user(userid):
    """Delete user in database"""

    user = User.query.get_or_404(userid)
    db.session.delete(user)
    db.session.commit()

    return redirect('/users')
