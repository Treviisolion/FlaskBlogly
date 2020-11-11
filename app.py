"""Blogly application."""

from flask_debugtoolbar import DebugToolbarExtension
from flask import Flask, redirect, render_template, request, send_file
from models import db, connect_db, User, Post, Tag, PostTag, DEFAULT_IMAGE

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

connect_db(app)

app.config['SECRET_KEY'] = 'JohnathonAppleseed452'
# app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
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

#########
# Users #
#########


@app.route('/users')
def show_users():
    """Show all users"""

    users = User.query.all()
    return render_template('users/users.html', users=users)


@app.route('/users/<int:userid>')
def show_user(userid):
    """Show a specific user"""

    user = User.query.get_or_404(userid)
    return render_template('users/user.html', user=user, posts=user.posts)


@app.route('/users/new', methods=['GET'])
def show_new_user_form():
    """Show the form for creating a new user"""

    return render_template('users/new_user.html')


@app.route('/users/new', methods=['POST'])
def create_user():
    """Creates a user"""

    first_name = request.form.get('first_name', None)
    last_name = request.form.get('last_name', None)
    image_url = request.form.get('image_url', None)

    # If information is somehow not provided, will show warnings to user
    missing_first_name = False
    missing_last_name = False
    if not first_name:
        missing_first_name = True
    if not last_name:
        missing_last_name = True
    if missing_first_name or missing_last_name:
        return render_template('users/new_user.html', missing_first_name=missing_first_name, missing_last_name=missing_last_name)

    if not image_url:
        new_user = User(first_name=first_name, last_name=last_name)
    else:
        new_user = User(first_name=first_name,
                        last_name=last_name, image_url=image_url)
    db.session.add(new_user)
    db.session.commit()

    return redirect(f'/users')


@app.route('/users/<int:userid>/edit', methods=['GET'])
def show_edit_user_form(userid):
    """Shows the form for editing the specified user"""

    user = User.query.get_or_404(userid)
    return render_template('users/edit_user.html', user=user)


@app.route('/users/<int:userid>/edit', methods=['POST'])
def edit_user(userid):
    """Edit user in database"""

    user = User.query.get_or_404(userid)
    first_name = request.form.get('first_name', None)
    last_name = request.form.get('last_name', None)
    image_url = request.form.get('image_url', None)

    user.update_user(first_name, last_name, image_url)
    db.session.commit()

    return redirect('/users')


@app.route('/users/<int:userid>/delete', methods=['POST'])
def delete_user(userid):
    """Delete user in database"""

    user = User.query.get_or_404(userid)
    db.session.delete(user)
    db.session.commit()

    return redirect('/users')

#########
# Posts #
#########


@app.route('/users/<int:userid>/posts/new', methods=['GET'])
def show_new_post_form(userid):
    """Shows the form for creating a new post for the specified user"""

    user = User.query.get_or_404(userid)
    tags = Tag.query.all()
    return render_template('posts/new_post.html', user=user, tags=tags)


@app.route('/users/<int:userid>/posts/new', methods=['POST'])
def create_post(userid):
    """Creates a new post for the specified user"""

    user = User.query.get_or_404(userid)
    title = request.form.get('title', None)
    content = request.form.get('content', None)
    tags = request.form.getlist('tags')

    # If information is somehow not provided, will show warnings to user
    missing_title = False
    missing_content = False
    if not title:
        missing_title = True
    if not content:
        missing_content = True
    if missing_title or missing_content:
        tags = Tag.query.all()
        return render_template('posts/new_post.html', user=user, missing_content=missing_content, missing_title=missing_title, tags=tags)

    new_post = Post(title=title, content=content, user_id=user.id)

    db.session.add(new_post)
    db.session.commit()

    for tag in tags:
        new_post_tag = PostTag(post_id=new_post.id, tag_id=int(tag))
        db.session.add(new_post_tag)

    db.session.commit()

    return redirect(f'/users/{userid}')


@app.route('/posts/<int:postid>')
def show_post(postid):
    """Shows the specified post"""

    post = Post.query.get_or_404(postid)
    return render_template('posts/post.html', post=post, user=post.user, tags=post.tags)


@app.route('/posts/<int:postid>/edit', methods=['GET'])
def show_edit_post_form(postid):
    """Shows the form for editing a post for the specified post"""

    post = Post.query.get_or_404(postid)
    tags = Tag.query.all()
    return render_template('posts/edit_post.html', post=post, user=post.user, tags=tags)


@app.route('/posts/<int:postid>/edit', methods=['POST'])
def edit_post(postid):
    """Edits the specified post"""

    post = Post.query.get_or_404(postid)
    post_tags = post.post_tags
    tags = Tag.query.all()
    title = request.form.get('title', None)
    content = request.form.get('content', None)
    checked_tags = request.form.getlist('tags')

    # Go through each tag and compare with checked tags
    for tag in tags:
        for checked_tag in checked_tags:
            # Check if the checked tag matches the tag, if so break and move onto the next tag
            if int(checked_tag) == tag.id:
                # Check if there already exits a posttag for the given post and tag
                for post_tag in post_tags:
                    if post_tag.tag_id == tag.id:
                        break
                # If a posttag was not found then create one
                else:
                    new_post_tag = PostTag(post_id=postid, tag_id=tag.id)
                    db.session.add(new_post_tag)
                break
        # If tag was not in checked_tags then check if tag is in post_tags
        else:
            for post_tag in post_tags:
                if post_tag.tag_id == tag.id:
                    db.session.delete(post_tag)
                    break

    db.session.commit()

    post.update_post(title, content)
    db.session.commit()

    return redirect(f'/posts/{postid}')


@app.route('/posts/<int:postid>/delete', methods=['POST'])
def delete_post(postid):
    """Deletes the specified post"""

    post = Post.query.get_or_404(postid)
    user = post.user
    db.session.delete(post)
    db.session.commit()

    return redirect(f'/users/{user.id}')

########
# Tags #
########


@app.route('/tags')
def show_tags():
    """Shows all the tags"""

    tags = Tag.query.all()
    return render_template('tags/tags.html', tags=tags)


@app.route('/tags/<int:tagid>')
def show_tag(tagid):
    """Shows the specified tag"""

    tag = Tag.query.get_or_404(tagid)
    posts = tag.posts
    return render_template('tags/tag.html', tag=tag, posts=posts)


@app.route('/tags/new', methods=['GET'])
def show_new_tag_form():
    """Shows the form for creating a new tag"""

    return render_template('tags/new_tag.html')


@app.route('/tags/new', methods=['POST'])
def create_tag():
    """Creates a tag"""

    name = request.form.get('tag_name', None)

    # If information is somehow not provided, will show warnings to user
    if not name:
        return render_template('tags/new_tag.html', missing_tag_name=True)

    new_tag = Tag(name=name)

    db.session.add(new_tag)
    db.session.commit()
    db.session.commit()

    return redirect('/tags')


@app.route('/tags/<int:tagid>/edit', methods=['GET'])
def show_edit_tag_form(tagid):
    """Shows the form to edit a tag"""

    tag = Tag.query.get_or_404(tagid)
    return render_template('tags/edit_tag.html', tag=tag)


@app.route('/tags/<int:tagid>/edit', methods=['POST'])
def edit_tag(tagid):
    """Edits the specified tag"""

    tag = Tag.query.get_or_404(tagid)
    name = request.form.get('tag_name', None)

    tag.update_tag(name)
    db.session.commit()

    return redirect('/tags')


@app.route('/tags/<int:tagid>/delete', methods=['POST'])
def delete_tag(tagid):
    """Deletes the specified tag"""

    tag = Tag.query.get_or_404(tagid)
    db.session.delete(tag)
    db.session.commit()
    return redirect('/tags')
