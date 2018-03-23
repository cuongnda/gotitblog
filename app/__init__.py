from flask_api import FlaskAPI
from flask_dance.consumer import oauth_authorized
from flask_dance.consumer.backend.sqla import SQLAlchemyBackend
from flask_dance.contrib.facebook import make_facebook_blueprint, facebook
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from flask_migrate import Migrate
from flask_security import SQLAlchemyUserDatastore, Security
from flask_dance.contrib.google import make_google_blueprint, google

from flask_sqlalchemy import SQLAlchemy
from flask import request, jsonify, abort, render_template, redirect, url_for, flash

# local import
from sqlalchemy.orm.exc import NoResultFound

from instance.config import app_config

# initialize sql-alchemy
db = SQLAlchemy()


def create_app(config_name):
    from app.models import BlogPost, User, Role, OAuth

    app = FlaskAPI(__name__, instance_relative_config=True)
    app.config.from_object(app_config[config_name])
    app.config.from_pyfile("config.py")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = "super-secret"

    app.config["SECURITY_POST_LOGIN"] = "/profile"

    db.init_app(app)
    # Setup Flask Migration
    migrate = Migrate(app, db)
    # Setup Flask-Security
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    security = Security(app, user_datastore)

    login_manager = LoginManager(app)
    login_manager.login_view = "my_login"

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    google_blueprint = make_google_blueprint(
        client_id="406704713101-d6a8tbbfq6cmmf16vtljh6gj71bn0ro9.apps.googleusercontent.com",
        client_secret="wvtkTq8IOxtOMHs2bvuN7kiV",
        scope=["profile", "email"]
    )
    google_blueprint.backend = SQLAlchemyBackend(OAuth, db.session, user=current_user)
    google_blueprint.backend.user_required = False
    app.register_blueprint(google_blueprint, url_prefix="/google_login")

    @app.route("/google")
    def google_login():
        if not google.authorized:
            return redirect(url_for("google.login"))
        account_info = google.get("/oauth2/v2/userinfo")
        account_info_json = account_info.json()
        app.logger.info("User with email %s logged in successfully" % account_info_json['email'])
        user = current_user
        response = jsonify({
            "status": "ok",
            "message": "User %s has been logged in successfully" % account_info_json['email'],
            "data": {
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "registration_completed": user.registration_completed(),
                    "type": user.type.code,
                    "phone": user.phone,
                    "name": user.name,
                    "occupation": user.occupation
                }
            }
        })
        response.status_code = 200
        return response

    @oauth_authorized.connect_via(google_blueprint)
    def google_logged_in(blueprint, token):
        if not token:
            app.logger.error("Failed to log in with Google.")
            return False

        account_info = blueprint.session.get("/oauth2/v2/userinfo")
        if not account_info.ok:
            app.logger.error("Failed to fetch user info from Google.")
            return False

        else:
            account_info_json = account_info.json()
            email = account_info_json["email"]

            query = User.query.filter_by(email=email)

            try:
                user = query.one()
                # If user is google user we log him in, if not we return False and redirect him to Facebook login page.
                if user.type == "facebook":
                    app.logger.info("User with email %s trying to sign in using Google account" % (email))
                    response = jsonify({
                        "status": "error",
                        "message": "The user with the same email has been registered with a Facebook account."
                                   " Please use Facebook to login!",
                        "data": {
                            "facebook_login_url": url_for("facebook_login"),
                            "google_login_url": url_for("google_login"),
                        }
                    })
                    response.status_code = 200
                    return response
                    # return redirect(url_for("facebook.login"))
                    # return False
            except NoResultFound:
                # If no user with existing email found, we create new user, mark him as Google user
                user = User(email=email, type="google", active=True)
                db.session.add(user)
                db.session.commit()

            login_user(user)
            app.logger.info("User with email %s logged in successfully" % account_info_json['email'])
            user = current_user
            response = jsonify({
                "status": "ok",
                "message": "User %s has been logged in successfully" % account_info_json['email'],
                "data": {
                    "user": {
                        "id": user.id,
                        "email": user.email,
                        "registration_completed": user.registration_completed(),
                        "type": user.type.code,
                        "phone": user.phone,
                        "name": user.name,
                        "occupation": user.occupation
                    }
                }
            })
            response.status_code = 200
            return response

    facebook_blueprint = make_facebook_blueprint(
        client_id="2032137377002819",
        client_secret="f4857526cfa52e0e390e1943dd636225",
        scope=["public_profile", "email"]
    )
    facebook_blueprint.backend = SQLAlchemyBackend(OAuth, db.session, user=current_user)
    facebook_blueprint.backend.user_required = False
    app.register_blueprint(facebook_blueprint, url_prefix="/facebook_login")

    @app.route("/facebook")
    def facebook_login():
        if not facebook.authorized:
            return redirect(url_for("facebook.login"))
        account_info = facebook.get("/me?fields=id,name,email")
        account_info_json = account_info.json()
        app.logger.info("User with email %s logged in successfully" % account_info_json['email'])
        user = current_user
        response = jsonify({
            "status": "ok",
            "message": "User %s has been logged in successfully" % account_info_json['email'],
            "data": {
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "registration_completed": user.registration_completed(),
                    "type": user.type.code,
                    "phone": user.phone,
                    "name": user.name,
                    "occupation": user.occupation
                }
            }
        })
        response.status_code = 200
        return response

    @oauth_authorized.connect_via(facebook_blueprint)
    def facebook_logged_in(blueprint, token):
        if not token:
            app.logger.error("Failed to log in with Facebook.")
            return False

        account_info = blueprint.session.get("/me?fields=id,name,email")
        if not account_info.ok:
            app.logger.error("Failed to fetch user info from Facebook.")
            return False

        else:
            account_info_json = account_info.json()
            email = account_info_json["email"]

            query = User.query.filter_by(email=email)

            try:
                user = query.one()
                # If user is facebook user we log him in, if not we return False and return error response.
                if user.type == "google":
                    app.logger.info("User with email %s trying to sign in using Facebook account" % (email))
                    response = jsonify({
                        "status": "error",
                        "message": "The user with the same email has been registered with a Google account."
                                   " Please use Google to login!",
                        "data": {
                            "facebook_login_url": url_for("facebook_login"),
                            "google_login_url": url_for("google_login"),
                        }
                    })
                    response.status_code = 200
                    return response

            except NoResultFound:
                # If no user with existing email found, we create new user, mark him as Facebook user
                user = User(email=email, type="facebook", active=True)
                db.session.add(user)
                db.session.commit()
        login_user(user)
        app.logger.info("User with email %s logged in successfully" % account_info_json['email'])
        user = current_user
        response = jsonify({
            "status": "ok",
            "message": "User %s has been logged in successfully" % account_info_json['email'],
            "data": {
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "registration_completed": user.registration_completed(),
                    "type": user.type.code,
                    "phone": user.phone,
                    "name": user.name,
                    "occupation": user.occupation
                }
            }
        })
        response.status_code = 200
        return response

    # Views
    @app.route("/")
    @login_required
    def home():
        posts = BlogPost.get_all()
        results = []

        for post in posts:
            obj = {
                "id": post.id,
                "title": post.title,
                "content": post.content,
                "date_created": post.date_created,
                "date_modified": post.date_modified
            }
            results.append(obj)
        response = jsonify(results)
        response.status_code = 200
        return response

    @app.route("/my_login")
    def my_login():
        response = jsonify({
            "facebook_login_url": url_for("facebook_login"),
            "google_login_url": url_for("google_login"),
        })
        response.status_code = 201
        return response

    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        return redirect(url_for("home"))

    # This is the end point for user to get/update his data
    @app.route("/me", methods=["GET", "PUT"])
    @login_required
    def user_manipulation(**kwargs):
        user = current_user
        if request.method == "GET":
            response = jsonify(user.to_dict())
            response.status_code = 200
            return response
        elif request.method == "PUT":
            name = str(request.data.get("name", ""))
            phone = str(request.data.get("phone", ""))
            occupation = str(request.data.get("occupation", ""))
            user.name = name
            user.phone = phone
            user.occupation = occupation
            user.save()
            response = jsonify(user.to_dict())
            response.status_code = 200
            return response

    # This is the end point for getting user data, this can be call from any user
    @app.route("/users", methods=["GET"])
    @login_required
    def users(**kwargs):
        if request.method == "GET":
            users = User.get_all()
            results = []

            for user in users:
                obj = user.to_dict()
                results.append(obj)
            response = jsonify(results)
            response.status_code = 200
            return response

    # This is the end point for getting user data, this can be call from any user
    @app.route("/users/<int:id>", methods=["GET"])
    @login_required
    def user(id, **kwargs):
        if request.method == "GET":
            user = User.query.filter_by(id=id).first()
            if not user:
                # Raise an HTTPException with a 404 not found status code
                abort(404)
            response = jsonify(user.to_dict())
            response.status_code = 200
            return response

    @app.route("/posts", methods=["POST", "GET"])
    @login_required
    def posts():
        user = current_user
        if request.method == "POST":
            # We only allow user to add post when his registration process is done
            if not user.registration_completed():
                response = jsonify({
                    "status": "error",
                    "message": "You did not finish your registration process. Please update your profile to continue!",
                    "data": user.to_dict()
                })
                response.status_code = 403
                return response

            title = str(request.data.get("title", ""))
            content = str(request.data.get("content", ""))
            if title:
                post = BlogPost(title=title, content=content)
                post.author_id = user.id
                post.save()
                response = jsonify(post.to_dict())
                response.status_code = 201
                return response
            else:
                response = jsonify({
                    "error": "Bad request"
                })
                response.status_code = 400
                return response
        else:
            # GET
            posts = BlogPost.get_all()
            results = []

            for post in posts:
                obj = post.to_dict()
                results.append(obj)
            response = jsonify(results)
            response.status_code = 200
            return response

    @app.route("/posts/<int:id>", methods=["GET", "PUT", "DELETE"])
    @login_required
    def post_manipulation(id, **kwargs):
        post = BlogPost.query.filter_by(id=id).first()
        if not post:
            # Raise an HTTPException with a 404 not found status code
            abort(404)

        if request.method == "DELETE":
            post.delete()
            return {
                       "message": "post {} deleted successfully".format(post.id)
                   }, 200

        elif request.method == "PUT":
            title = str(request.data.get("title", ""))
            post.title = title
            post.save()
            response = jsonify(post.to_dict)
            response.status_code = 200
            return response
        else:
            response = jsonify(post.to_dict())
            response.status_code = 200
            return response

    @app.route("/posts/<int:id>/like")
    @login_required
    def like(id, **kwargs):
        """Perform a like action from current user"""
        post = BlogPost.query.filter_by(id=id).first()
        if not post:
            # Raise an HTTPException with a 404 not found status code
            abort(404)
        user = current_user
        post.like_by(user.id)
        post.save()
        response = jsonify(post.to_dict())
        response.status_code = 200
        return response

    return app
