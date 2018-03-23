from flask import abort, json
from flask_dance.consumer.backend.sqla import OAuthConsumerMixin
from flask_security import UserMixin, RoleMixin
from sqlalchemy_utils import ChoiceType

from app import db

USER_TYPES = [
    (u'facebook', u'Facebook'),
    (u'google', u'Google')
]

roles_users = db.Table('roles_users',
                       db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
                       db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))


class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))
    type = db.Column(ChoiceType(USER_TYPES))
    phone = db.Column(db.String(255))
    name = db.Column(db.String(255))
    occupation = db.Column(db.String(255))

    def registration_completed(self):
        """Check if user finish the registration process"""
        if self.type == "facebook":
            return not ((not self.phone) and (not self.name))
        elif self.type == "google":
            return not (not self.occupation)
        return False

    @staticmethod
    def get_all():
        return User.query.all()

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def to_dict(self):
        result = {
            "id": self.id,
            "email": self.email,
            "registration_completed": self.registration_completed(),
            "type": self.type.code,
            "phone": self.phone,
            "name": self.name,
            "occupation": self.occupation
        }
        return result

    def to_json(self):
        return json.dumps(self.to_dict(), indent=4, sort_keys=True, default=str)

    def __repr__(self):
        return "<User: {}>".format(self.email)


class OAuth(OAuthConsumerMixin, db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    user = db.relationship(User)


likes = db.Table('likes',
                 db.Column('post_id', db.Integer, db.ForeignKey("blog_post.id"), primary_key=True),
                 db.Column('user_id', db.Integer, db.ForeignKey(User.id), primary_key=True)
                 )

class BlogPost(db.Model):
    """This class represents the Blog Post table."""

    __tablename__ = 'blog_post'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(
        db.DateTime, default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp())
    content = db.Column(db.Text)

    author_id = db.Column(db.Integer, db.ForeignKey(User.id))
    author = db.relationship(User)

    likes = db.relationship('User', secondary=likes, lazy='subquery',
                            backref=db.backref('posts', lazy=True))

    def __init__(self, title, content):
        """initialize with title."""
        self.title = title
        self.content = content

    def like_by(self, user_id):
        user = User.query.filter_by(id=user_id).first()
        if user:
            self.likes.append(user)
        else:
            abort(404)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def to_dict(self):
        like_users = [user.id for user in self.likes]
        result = {
            "id": self.id,
            "title": self.title,
            "date_created": self.date_created,
            "date_modified": self.date_modified,
            "author_id": self.author_id,
            "likes": like_users
        }
        return result

    def to_json(self):
        return json.dumps(self.to_dict(), indent=4, sort_keys=True, default=str)

    @staticmethod
    def get_all():
        return BlogPost.query.all()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return "<BlogPost: {}>".format(self.title)
