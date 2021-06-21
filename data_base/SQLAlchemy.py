from hafifa.data_base.DB import DB
from hafifa.singleton import Singleton
import hafifa.data_base.data_models


class SQLAlchemyHandler(metaclass=Singleton):
    def __init__(self, app):
        self.db = DB.db
        self.db.init_app(app)

    def create_data_models(self):
        self.db.create_all()

    def clear_data_models(self):
        self.db.drop_all()
