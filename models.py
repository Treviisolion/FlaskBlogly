"""Models for Blogly."""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

db = SQLAlchemy()

DEFAULT_IMAGE = '/static/uploads/default_user.png'

def connect_db(app):
    """Connect to database."""

    db.app = app
    db.init_app(app)


class User(db.Model):
    """User"""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    image_url = db.Column(
        db.String(), default=DEFAULT_IMAGE)

    posts = db.relationship('Post', cascade="all, delete-orphan")

    def update_user(self, first, last, url):
        """Updates the user with the provided information, if parameter is set to None will not update that field"""

        if first:
            self.first_name = first
        if last:
            self.last_name = last
        if url:
            self.image_url = url


class Post(db.Model):
    """Post"""

    __tablename__ = "post"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(128), nullable=False)
    content = db.Column(db.String(), nullable=False)
    created_at = db.Column(db.TIMESTAMP(timezone=True),
                           nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    user = db.relationship('User')
    post_tags = db.relationship('PostTag', cascade="all, delete-orphan")

    def update_post(self, title, content):
        """Updates the post with the provided information, if parameter is set to None will not update that field"""

        if title:
            self.title = title
        if content:
            self.content = content

class Tag(db.Model):
    """tag"""

    __tablename__="tag"

    id = db.Column(db.Integer,primary_key=True, autoincrement=True)
    name = db.Column(db.String(), nullable=False, unique=True)

    posts = db.relationship('Post', secondary='post_tag', backref='tags')

    def update_tag(self, name):
        """Updates the tag with the provided information, if parameter is set to None will not update that field"""

        if name:
            self.name = name

class PostTag(db.Model):
    """PostTag"""

    __tablename__="post_tag"

    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), primary_key=True)
    tag_id = db.Column(db.Integer, db.ForeignKey('tag.id'), primary_key=True)