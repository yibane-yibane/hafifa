from sqlalchemy import Column, String, Integer, ForeignKey
from hafifa.data_base.DB import DB


class Frame(DB.db.Model):
    __tablename__ = 'frames'
    id = Column(Integer, primary_key=True, autoincrement=True)
    video_id = Column(Integer, ForeignKey('videos.id'))
    metadata_id = Column(Integer, ForeignKey('metadata.id'))
    os_path = Column(String)
    index = Column(Integer)

    def set_metadata_id(self, metadata_id: int):
        self.metadata_id = metadata_id
