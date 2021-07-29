from sqlalchemy import exists
from hafifa.data_base.DB import DB
from hafifa.singleton import Singleton
import hafifa.data_base.data_models as data_models
from  hafifa.data_base.query_creator import create_query


class SQLAlchemyHandler(metaclass=Singleton):
    def __init__(self):
        self.db = DB.db

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

    def is_data_model_exists(self, data_model: DB.db.Model, where_section: dict):
        """
        Check if data model instance exists in db.
        :param data_model: Data model/table the instance belong.
        :param where_section: The query where section.
        :return: True/False.
        """
        exists_query = exists(data_model)

        for field, value in where_section.items():
            exists_query = exists_query.where(getattr(data_model, field) == value)

        return self.db.session.query(exists_query).scalar()

    def get_entities(self, select_section: list, attributes_filters: dict, count=0):
        """
        Get entities from database.
        :param select_section: The query select section.
        :param attributes_filters: The query filter dictionary.
        :param count: How many to get 0 mean all.
        :return: The entities from the query.
        """
        query = create_query(self.db.session.query(), select_section, attributes_filters)

        if count == 1:
            return query.first()
        elif count > 1:
            return query.limit(count).all()
        else:
            return query.all()
