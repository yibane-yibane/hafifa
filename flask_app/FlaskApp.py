from flask import Flask
from hafifa.app_wrap.FlaskConfig import FlaskConfig
from hafifa.data_base_wrap.SQLAlchemyWrapper import SQLAlchemyWrapper


class FlaskAppWrapper:
    def __init__(self):
        self.app = Flask(__name__, instance_relative_config=False)
        self.app.config.from_object(FlaskConfig)
        self.db = SQLAlchemyWrapper(self.app)

    def init_database(self):
        with self.app.app_context():
            self.db.create_data_models()
