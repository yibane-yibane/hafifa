from sqlalchemy import Column, String, Integer, ForeignKey
from hafifa.data_base.DB import DB
from hafifa.singleton import Singleton


class Frame(DB.db.Model):
    __tablename__ = 'frames'
    id = Column(Integer, primary_key=True)
    video_id = Column(String, ForeignKey('videos.id'))
    metadata_id = Column(Integer, ForeignKey('metadata.id'))
    os_path = Column(String)
    index = Column(Integer)
