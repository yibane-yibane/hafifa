from flask import Flask
from hafifa.flask_app.FlaskConfig import FlaskConfig
from hafifa.data_base.SQLAlchemy import SQLAlchemyHandler


class FlaskAppHandler:
    def __init__(self):
        self.app = Flask(__name__, instance_relative_config=False)
        self.app.config.from_object(FlaskConfig)
        self.db = SQLAlchemyHandler(self.app)

    def init_database(self):
        with self.app.app_context():
            self.db.clear_data_models()
            self.db.create_data_models()
