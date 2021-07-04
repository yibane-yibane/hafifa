from sqlalchemy import Column, String, Integer
from hafifa.data_base.DB import DB


class Video(DB.db.Model):
    __tablename__ = 'videos'
    id = Column(String, primary_key=True)
    observation_name = Column(String)
    os_path = Column(String)
    number_of_frames = Column(Integer)

    def __init__(self, video_id, observation_name, os_path, number_of_frames):
        self.id = video_id
        self.observation_name = observation_name
        self.os_path = os_path
        self.number_of_frames = number_of_frames
