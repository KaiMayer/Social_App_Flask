from flask import Flask
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import config

bootstrap = Bootstrap()
moment = Moment()
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'authentication.login'


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .authentication import authentication as authentication_blueprint
    app.register_blueprint(authentication_blueprint, url_prefix='/authentication')

    from .users import users as users_blueprint
    app.register_blueprint(users_blueprint, url_prefix='/users')

    return app

