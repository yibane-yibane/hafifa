from sqlalchemy import Column, String, Integer, ForeignKey
from hafifa.data_base.DB import DB


class Frame(DB.db.Model):
    __tablename__ = 'frames'
    id = Column(String, primary_key=True)
    video_id = Column(String, ForeignKey('videos.id'))
    metadata_id = Column(String)
    os_path = Column(String)
    index = Column(Integer)

    def __init__(self, frame_id, video_id, os_path, index):
        self.id = frame_id
        self.video_id = video_id
        self.os_path = os_path
        self.index = index

    def set_metadata_id(self, metadata_id):
        self.metadata_id = metadata_id
