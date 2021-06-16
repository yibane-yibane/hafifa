from sqlalchemy import Column, Float, Boolean, Integer
from hafifa import db


class Metadata(db.Model):
    __tablename__ = 'metadata'
    id = Column(Integer, primary_key=True)
    tag = Column(Boolean)
    fov = Column(Float)
    azimuth = Column(Float)
    elevation = Column(Float)
