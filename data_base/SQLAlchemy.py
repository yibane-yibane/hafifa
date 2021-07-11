from hafifa.data_base.DB import DB
from hafifa.singleton import Singleton
import hafifa.data_base.data_models as data_models


class SQLAlchemyHandler(metaclass=Singleton):
    def __init__(self, app):
        self.db = DB.db
        self.db.init_app(app)

    def create_data_models(self):
        self.db.create_all()

    def clear_data_models(self):
        self.db.drop_all()

    def insert_one(self, table_instance):
        self.db.session.add(table_instance)
        self.db.session.commit()

    def insert_many(self, table_instances: list):
        self.db.session.add_all(table_instances)
        self.db.session.commit()

    def get_metadata(self, fov: float, azimuth: float, elevation: float, tag: bool):
        return self.db.session.query(data_models.Metadata) \
            .filter(data_models.Metadata.fov == fov) \
            .filter(data_models.Metadata.azimuth == azimuth) \
            .filter(data_models.Metadata.elevation == elevation) \
            .filter(data_models.Metadata.tag == tag).first()

    def get_video(self, observation_name: str, os_path: str, number_of_frames: int):
        return self.db.session.query(data_models.Video) \
            .filter(data_models.Video.observation_name == observation_name) \
            .filter(data_models.Video.os_path == os_path) \
            .filter(data_models.Video.number_of_frames == number_of_frames).first()
