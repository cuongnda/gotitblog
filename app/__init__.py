from flask_api import FlaskAPI

from flask_dance.consumer import oauth_authorized
from flask_dance.consumer.backend.sqla import SQLAlchemyBackend
from flask_dance.contrib.facebook import make_facebook_blueprint, facebook
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from flask_migrate import Migrate
from flask_security import SQLAlchemyUserDatastore, Security
from flask_dance.contrib.google import make_google_blueprint, google

from flask_sqlalchemy import SQLAlchemy
from flask import request, jsonify, abort, render_template, redirect, url_for, flash, Flask
from flask_restful import Api

# local import
from sqlalchemy.orm.exc import NoResultFound

from instance.config import app_config

# initialize sql-alchemy
db = SQLAlchemy()


def create_app(config_name):
    from app.models import BlogPost, User, Role, OAuth
    from app.resources import Post, PostList, UserResource, UserList, Like
    # app = FlaskAPI(__name__, instance_relative_config=True)
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(app_config[config_name])
    app.config.from_pyfile("config.py")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = "super-secret"

    db.init_app(app)
    # Setup Flask Migration
    migrate = Migrate(app, db)

    api = Api(app)
    api.add_resource(Post, "/posts/<int:post_id>")
    api.add_resource(PostList, "/posts")
    api.add_resource(UserResource, "/users/<int:user_id>")
    api.add_resource(UserList, "/users")
    api.add_resource(Like, "/posts/<int:post_id>/like")
    # Setup Flask-Security
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    security = Security(app, user_datastore)

    login_manager = LoginManager(app)
    login_manager.login_view = "my_login"

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    google_blueprint = make_google_blueprint(
        client_id=app.config['GOOGLE_API_CLIENT_ID'],
        client_secret=app.config['GOOGLE_API_CLIENT_ID'],
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
        client_id=app.config['FACEBOOK_API_CLIENT_ID'],
        client_secret=app.config['FACEBOOK_API_CLIENT_SECRETE'],
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
            "status": "error",
            "message": "Login Required",
            "data": {

                "facebook_login_url": url_for("facebook_login"),
                "google_login_url": url_for("google_login"),
            }
        })
        response.status_code = 403
        return response

    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        return redirect(url_for("home"))

    return app
