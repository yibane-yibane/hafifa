from sqlalchemy import Column, String, Integer
from hafifa.data_base.DB import DB
from hafifa.singleton import Singleton


class Video(DB.db.Model):
    __tablename__ = 'videos'
    id = Column(String, primary_key=True)
    observation_name = Column(String)
    os_path = Column(String)
    number_of_frames = Column(Integer)
