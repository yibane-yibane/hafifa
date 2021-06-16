from flask import Flask
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

from hafifa.data_models.Frame import Frame
from hafifa.data_models.Video import Video
from hafifa.data_models.Metadata import Metadata


def init_app():
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object('config.Config')

    db.init_app(app)

    with app.app_context():
        db.create_all()
        return app
