from sqlalchemy import Column, String, Integer
from hafifa.data_base.DB import DB


class Video(DB.db.Model):
    __tablename__ = 'videos'
    id = Column(Integer, primary_key=True, autoincrement=True)
    observation_name = Column(String)
    os_path = Column(String)
    number_of_frames = Column(Integer)
