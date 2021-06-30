from sqlalchemy import Column, Float, Boolean, Integer
from hafifa.data_base.DB import DB
from hafifa.singleton import Singleton


class Metadata(DB.db.Model):
    __tablename__ = 'metadata'
    id = Column(Integer, primary_key=True)
    tag = Column(Boolean)
    fov = Column(Float)
    azimuth = Column(Float)
    elevation = Column(Float)
