import os
import cv2
import asyncio
import hafifa.utils.utils as utils
import hafifa.data_base.data_models as dm
from uuid import uuid4
from flask import Flask, request
from hafifa.singleton import Singleton
from hafifa.logger.logger import Logger
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
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
        video_id = uuid4()
        video_file_name = os.path.basename(path)
        image_list = utils.extract_video_to_frames(path)

        Logger.logger.info(f'Start upload video for path: {path}')
        upload_video_task = asyncio.create_task(self.upload_video(path, video_file_name))

        Logger.logger.info(f'Start upload images for path: {path}')
        thread_pool = ThreadPoolExecutor(max_workers=5)
        thread_pool.submit(self.upload_images, image_list, video_file_name)

        frame_list = self.create_frames(image_list, video_id, video_file_name)

        observation = os.path.basename(path).split('_')[0]
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

    async def upload_video(self, path, video_file_name):
        with open(path, 'rb') as file:
            self.azure_handler.upload_file(video_file_name, file, 'videos/')

    def upload_images(self, image_list, video_file_name):
        for index, image in enumerate(image_list):
            _, img_encode = cv2.imencode('.jpg', image)
            img_bytes = img_encode.tobytes()
            self.azure_handler.upload_file(f'frame{index}.jpg', img_bytes, os.path.join('frames', video_file_name))

    def create_frames(self, image_list, video_id, video_name):
        return [dm.Frame(str(uuid4()), str(video_id), self.create_frame_os_path(video_name, index), index)
                for index, frame in enumerate(image_list)]

    def create_frame_os_path(self, video_name, index):
        return os.path.join("frames", video_name, f'frame{index}.jpg')

    def get_metadata_list_and_set_metadata_for_each_frame(self, frame_list, image_list):
        metadata_list = list()
        for index, image in enumerate(image_list):
            fov, azi, lev = utils.generate_metadata(image)
            tag = utils.is_frame_tagged(image)

            metadata_id = '-'.join(map(str, [fov, azi, lev, tag]))
            frame_list[index].set_metadata_id(metadata_id)

            if not [metadata for metadata in metadata_list if metadata.id == metadata_id] and \
               not self.db.get_by_id(dm.Metadata, metadata_id):
                metadata_list.append(dm.Metadata(metadata_id, fov, azi, lev, tag))

        return metadata_list

    def insert_to_database(self, video, metadata_list, frame_list):
        with self.app.app_context():
            self.db.insert_one(video)
            self.db.insert_many(metadata_list)
            self.db.insert_many(frame_list)
