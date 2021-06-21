from hafifa.data_base.base import db
import hafifa.data_base.data_models


class SQLAlchemyHandler:
    def __init__(self, app):
        self.db = db
        self.db.init_app(app)

    def create_data_models(self):
        self.db.create_all()

    def clear_data_models(self):
        self.db.drop_all()
