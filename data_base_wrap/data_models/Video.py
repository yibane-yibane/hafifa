from sqlalchemy import Column, String, Integer
from hafifa.data_base_wrap.base import Base


class Video(Base):
    __tablename__ = 'videos'
    id = Column(String, primary_key=True)
    observation_name = Column(String)
    os_path = Column(String)
    frames_number = Column(Integer)
