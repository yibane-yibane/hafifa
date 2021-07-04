from sqlalchemy import Column, Float, Boolean, String
from hafifa.data_base.DB import DB


class Metadata(DB.db.Model):
    __tablename__ = 'metadata'
    id = Column(String, primary_key=True)
    fov = Column(Float)
    azimuth = Column(Float)
    elevation = Column(Float)
    tag = Column(Boolean)

    def __init__(self, metadata_id: str, fov: float, azimuth: float, elevation: float, tag: bool):
        self.id = metadata_id
        self.tag = tag
        self.fov = fov
        self.azimuth = azimuth
        self.elevation = elevation
