import os
import cv2
import asyncio
import hafifa.utils.utils as utils
import hafifa.data_base.data_models as dm
from uuid import uuid4
from flask import Flask, request
from hafifa.singleton import Singleton
from hafifa.logger.logger import Logger
from concurrent.futures import ThreadPoolExecutor
from hafifa.flask_app.FlaskConfig import FlaskConfig
from hafifa.data_base.SQLAlchemy import SQLAlchemyHandler
from hafifa.object_store.azure_handler import AzureBlobHandler


class FlaskAppHandler(metaclass=Singleton):
    def __init__(self):
        self.app = Flask(__name__, instance_relative_config=False)
        self.app.config.from_object(FlaskConfig)
        self.db = SQLAlchemyHandler(self.app)
        self.azure_handler = AzureBlobHandler()
        self.azure_handler.create_container()

    def init_database(self):
        with self.app.app_context():
            self.db.clear_data_models()
            self.db.create_data_models()

    def run(self):
        self.app.add_url_rule('/handle_video', view_func=self.handle_video, methods=['POST'])
        self.app.run()

    async def handle_video(self):
        path = request.json['video_path']
        Logger.logger.info(f'Start handle path: {path}')
        video_id = str(uuid4())
        video_file_name = os.path.basename(path)
        image_list = utils.extract_video_to_frames(path)

        Logger.logger.info(f'Start upload video for path: {path}')
        upload_video_task = asyncio.create_task(self.upload_video(path, video_file_name))

        Logger.logger.info(f'Start upload images for path: {path}')
        thread_pool = ThreadPoolExecutor(max_workers=5)
        thread_pool.submit(self.upload_images, image_list, video_file_name)

        frame_list = self.create_frames(image_list, video_id, video_file_name)

        observation = self.get_observation_name(path)
        video = dm.Video(str(video_id), observation, video_file_name, len(frame_list))

        metadata_list = self.get_metadata_list_and_set_metadata_for_each_frame(frame_list, image_list)

        Logger.logger.info(f'Start insert video and frames to database, video path: {path}')
        thread_pool.submit(self.insert_to_database, video, metadata_list, frame_list)

        thread_pool.shutdown(wait=True)
        await upload_video_task

        Logger.logger.info(f'finish upload video for path: {path}')
        Logger.logger.info(f'finish upload images for path: {path}')
        Logger.logger.info(f'Finish insert video and frames to database, video path: {path}')
        Logger.logger.info(f'Finish handle path: {path}')

    async def upload_video(self, path: str, video_file_name: str):
        with open(path, 'rb') as file:
            self.azure_handler.upload_file(video_file_name, file, 'videos/')

    def upload_images(self, images: list, video_file_name: str):
        for index, image in enumerate(images):
            _, img_encode = cv2.imencode('.jpg', image)
            img_bytes = img_encode.tobytes()
            self.azure_handler.upload_file(f'frame{index}.jpg', img_bytes, os.path.join('frames', video_file_name))

    def create_frames(self, images: list, video_id: str, video_name: str):
        return [dm.Frame(str(uuid4()), video_id, self.create_frame_os_path(video_name, index), index)
                for index, frame in enumerate(images)]

    def create_frame_os_path(self, video_name: str, index: int):
        return os.path.join("frames", video_name, f'frame{index}.jpg')

    def get_observation_name(self, path: str):
        return os.path.basename(path).split('_')[0]

    def get_metadata_list_and_set_metadata_for_each_frame(self, frames: list, images: list):
        metadata_list = list()
        for index, image in enumerate(images):
            fov, azi, lev = utils.generate_metadata(image)
            tag = utils.is_frame_tagged(image)

            metadata_id = self.get_metadata_id(fov, azi, lev, tag)
            frames[index].set_metadata_id(metadata_id)

            if not self.is_metadata_already_exists(metadata_list, metadata_id):
                metadata_list.append(dm.Metadata(metadata_id, fov, azi, lev, tag))

        return metadata_list

    def get_metadata_id(self, fov, azi, lev, tag):
        return '-'.join(map(str, [fov, azi, lev, tag]))

    def is_metadata_already_exists(self, metadatas: list, metadata_id: str):
        return not self.get_metadata_by_id(metadatas, metadata_id) and not self.db.get_by_id(dm.Metadata, metadata_id)

    def get_metadata_by_id(self, metadatas: list, metadata_id: str):
        return [metadata for metadata in metadatas if metadata.id == metadata_id]

    def insert_to_database(self, video: dm.Video, metadatas: list, frames: list):
        with self.app.app_context():
            self.db.insert_one(video)
            self.db.insert_many(metadatas)
            self.db.insert_many(frames)
