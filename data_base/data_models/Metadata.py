from sqlalchemy import Column, Float, Boolean, Integer
from hafifa.data_base.DB import DB


class Metadata(DB.db.Model):
    __tablename__ = 'metadata'
    id = Column(Integer, primary_key=True, autoincrement=True)
    fov = Column(Float)
    azimuth = Column(Float)
    elevation = Column(Float)
    tag = Column(Boolean)
