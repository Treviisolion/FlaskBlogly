"""Models for Blogly."""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def connect_db(app):
    """Connect to database."""

    db.app = app
    db.init_app(app)


class User(db.Model):
    """User"""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(), nullable=False)
    last_name = db.Column(db.String(), nullable=False)
    image_url = db.Column(
        db.String(), default='/static/uploads/default_user.png')

    def update_user(self, first, last, url):
        """Updates the user with the provided information, if parameter is set to None will not update that field"""

        if first:
            self.first_name = first
        if last:
            self.last_name = last
        if url:
            self.image_url = url
