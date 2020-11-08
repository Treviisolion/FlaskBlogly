"""Blogly application."""

from flask_debugtoolbar import DebugToolbarExtension
from flask import Flask, redirect, render_template, request, send_file
from models import db, connect_db, User, Post, DEFAULT_IMAGE

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

connect_db(app)

app.config['SECRET_KEY'] = 'JohnathonAppleseed452'
# app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
# debug = DebugToolbarExtension(app)

db.create_all()


@app.route('/')
def redirect_to_users():
    """Main page is /users redirect to there"""

    return redirect('/users')


@app.route(DEFAULT_IMAGE)
def return_default_user():
    """Returns the default user profile"""

    return send_file(DEFAULT_IMAGE[1:])


@app.route('/users')
def show_users():
    """Show all users"""

    users = User.query.all()
    return render_template('users.html', users=users)


@app.route('/users/<userid>')
def show_user(userid):
    """Show a specific user"""

    user = User.query.get_or_404(userid)
    return render_template('user.html', user=user, posts=user.posts)


@app.route('/users/new', methods=['GET'])
def show_new_user_form():
    """Show the form for creating a new user"""

    return render_template('new_user.html')


@app.route('/users/new', methods=['POST'])
def create_user():
    """Creates a user"""

    first_name = request.form.get('first_name', None)
    last_name = request.form.get('last_name', None)
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
    """Shows the form for editing the specified user"""

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


@app.route('/users/<userid>/posts/new', methods=['GET'])
def show_new_post_form(userid):
    """Shows the form for creating a new post for the specified user"""

    user = User.query.get_or_404(userid)
    return render_template('new_post.html', user=user)


@app.route('/users/<userid>/posts/new', methods=['POST'])
def create_post(userid):
    """Creates a new post for the specified user"""

    user = User.query.get_or_404(userid)
    title = request.form.get('title', None)
    content = request.form.get('content', None)

    new_post = Post(title=title, content=content, user_id=user.id)

    db.session.add(new_post)
    db.session.commit()

    return redirect(f'/users/{userid}')


@app.route('/posts/<postid>')
def show_post(postid):
    """Shows the specified post"""

    post = Post.query.get_or_404(postid)
    return render_template('post.html', post=post, user=post.user)


@app.route('/posts/<postid>/edit', methods=['GET'])
def show_edit_post_form(postid):
    """Shows the form for editing a post for the specified post"""

    post = Post.query.get_or_404(postid)
    return render_template('edit_post.html', post=post, user=post.user)


@app.route('/posts/<postid>/edit', methods=['POST'])
def edit_post(postid):
    """Edits the specified post"""

    post = Post.query.get_or_404(postid)
    title = request.form.get('title', None)
    content = request.form.get('content', None)

    post.update_post(title, content)
    db.session.commit()

    return redirect(f'/posts/{postid}')

@app.route('/posts/<postid>/delete', methods=['POST'])
def delete_post(postid):
    """Deletes the specified post"""

    post = Post.query.get_or_404(postid)
    user = post.user
    db.session.delete(post)
    db.session.commit()

    return redirect(f'/users/{user.id}')