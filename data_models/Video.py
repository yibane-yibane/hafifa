from sqlalchemy import Column, String, Integer
from hafifa import db


class Video(db.Model):
    __tablename__ = 'videos'
    id = Column(String, primary_key=True)
    viewpoint_name = Column(String)
    os_path = Column(String)
    frames_number = Column(Integer)
