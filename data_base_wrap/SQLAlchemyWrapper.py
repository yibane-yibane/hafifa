from sqlalchemy import create_engine
from hafifa.data_base_wrap.SQLAlchemyConfig import SQLAlchemyConfig
from hafifa.data_base_wrap.base import Base
import hafifa.data_base_wrap.data_models


class SQLAlchemyWrapper:
    def __init__(self):
        self.engine = create_engine(SQLAlchemyConfig.SQLALCHEMY_DATABASE_URI, echo=True)

    def create_tables(self):
        Base.metadata.create_all(self.engine)
