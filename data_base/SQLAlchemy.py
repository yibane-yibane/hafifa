from hafifa.data_base.DB import DB
from hafifa.singleton import Singleton
import hafifa.data_base.data_models as dm


class SQLAlchemyHandler(metaclass=Singleton):
    def __init__(self, app):
        self.db = DB.db
        self.db.init_app(app)

    def create_data_models(self):
        self.db.create_all()

    def clear_data_models(self):
        self.db.drop_all()

    def insert_one(self, table_instance):
        self.db.session.add(table_instance)
        self.db.session.commit()

    def insert_many(self, table_instances):
        self.db.session.add_all(table_instances)
        self.db.session.commit()

    def get_by_id(self, table, instance_id):
        return table.query.filter(table.id == instance_id).first()
