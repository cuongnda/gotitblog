from flask import request, abort
from flask_login import current_user, login_required
from flask_restful import Resource, reqparse

from app.models import BlogPost, User
from app.utils import finish_registration_required

parser = reqparse.RequestParser()
parser.add_argument('title')
parser.add_argument('content')
parser.add_argument('name')
parser.add_argument('phone')
parser.add_argument('occupation')
parser.add_argument('user_id')


class UserResource(Resource):
    @login_required
    def get(self, user_id):
        user = User.query.filter_by(id=user_id).first()
        if not user:
            # Raise an HTTPException with a 404 not found status code
            abort(404)
        return user.to_json()

    @login_required
    def put(self, user_id):
        user = User.query.filter_by(id=user_id).first()
        if not user:
            # Raise an HTTPException with a 404 not found status code
            abort(404)

        # We only user to edit him self
        if user.id != current_user.id:
            abort(403)
        args = parser.parse_args()
        name = args["name"]
        phone = args["phone"]
        occupation = args["occupation"]
        user.name = name
        user.phone = phone
        user.occupation = occupation
        user.save()

        return user.to_json()


class UserList(Resource):
    @login_required
    @finish_registration_required
    def get(self):
        users = User.get_all()
        results = []
        for user in users:
            obj = user.to_json()
            results.append(obj)
        return results


class Post(Resource):
    @login_required
    @finish_registration_required
    def get(self, post_id):
        post = BlogPost.query.filter_by(id=post_id).first()
        if not post:
            abort(404)
        return post.to_json()

    @login_required
    @finish_registration_required
    def put(self, post_id):
        post = BlogPost.query.filter_by(id=post_id).first()
        post.title = request.form['title']
        post.save()
        return post.to_json()

    @login_required
    @finish_registration_required
    def delete(self, post_id):
        post = BlogPost.query.filter_by(id=post_id).first()
        #User should only be allowed to delete his post
        if post.author_id != current_user.id:
            abort(403)
        post.delete()
        return {"status": "ok",
                "message": "Post is deleted successfully"}


class PostList(Resource):
    @login_required
    @finish_registration_required
    def get(self):
        posts = BlogPost.get_all()
        results = []

        for post in posts:
            obj = post.to_json()
            results.append(obj)
        return results

    @login_required
    @finish_registration_required
    def post(self):
        user = current_user
        args = parser.parse_args()
        title = args['title']
        content = args['content']
        if title:
            post = BlogPost(title=title, content=content)
            post.author_id = user.id
            post.save()
            response = post.to_json()
            return response, 201


class Like(Resource):
    """This end point simply perform a like request"""
    @login_required
    @finish_registration_required
    def post(self, post_id):
        """Perform a like action from current user"""
        post = BlogPost.query.filter_by(id=post_id).first()
        if not post:
            # Raise an HTTPException with a 404 not found status code
            abort(404)
        user = current_user
        post.like_by(user.id)
        post.save()
        return post.to_json()
