from flask_sqlalchemy import SQLAlchemy
from hafifa.singleton import Singleton


class DB(metaclass=Singleton):
    db = SQLAlchemy()
