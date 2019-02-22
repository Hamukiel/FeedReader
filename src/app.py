from flask import Flask

from src.feed.blueprint import mod_feed


def create_app():
    app = Flask(__name__)
    app.register_blueprint(mod_feed)
    return app
