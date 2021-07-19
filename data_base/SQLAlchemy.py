from sqlalchemy import exists

from hafifa.data_base.DB import DB
from hafifa.singleton import Singleton
import hafifa.data_base.data_models as data_models


class SQLAlchemyHandler(metaclass=Singleton):
    def __init__(self, app):
        self.db = DB.db
        self.db.init_app(app)

    def create_data_models(self):
        self.db.create_all()

    def clear_data_models(self):
        self.db.drop_all()

    def init_database(self):
        self.clear_data_models()
        self.create_data_models()

    def insert_one(self, table_instance: DB.db.Model):
        self.db.session.add(table_instance)
        self.db.session.commit()

    def insert_many(self, table_instances: list):
        self.db.session.add_all(table_instances)
        self.db.session.commit()

    def get_one(self, data_model, attributes_filters: dict):
        query = self.db.session.query(data_model)

        for model_and_attr, value in attributes_filters.items():
            query = query.filter(model_and_attr == value)

        return query.first()

    def is_data_model_exists(self, data_model: DB.db.Model, where_section: dict):
        """
        Check if data model instance exists in db.
        :param data_model: Data model/table the instance belong.
        :param where_section: The query where section.
        :return: True/False.
        """
        exists_query = exists(data_model)

        for field, value in where_section.items():
            exists_query = exists_query.where(field == value)

        return self.db.session.query(exists_query).scalar()
