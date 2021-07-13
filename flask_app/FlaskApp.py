import json
import os
import cv2
import asyncio
import hafifa.utils.metadata_utils as metadata_utils
import hafifa.utils.frame_utils as frame_utils
import hafifa.data_base.data_models as data_models
import hafifa.utils.insert_data_models_db_utils as video_handle
from flask import Flask, request
from hafifa.singleton import Singleton
from hafifa.logger.logger import Logger
from concurrent.futures import ThreadPoolExecutor
from hafifa.flask_app.FlaskConfig import FlaskConfig
from hafifa.data_base.SQLAlchemy import SQLAlchemyHandler
from hafifa.object_storage.azure_container_handler import AzureBlobContainerHandler


class FlaskAppHandler(metaclass=Singleton):
    def __init__(self):
        self.app = Flask(__name__, instance_relative_config=False)
        self.app.config.from_object(FlaskConfig)
        self.db = SQLAlchemyHandler(self.app)
        self.azure_container_handler = AzureBlobContainerHandler()

    def init_database(self):
        """
        Initiate database clear data models and create them
        """
        with self.app.app_context():
            self.db.clear_data_models()
            self.db.create_data_models()

    def run(self):
        self.app.add_url_rule('/upload_video', view_func=self.upload_video, methods=['POST'])
        self.app.run()

    async def upload_video(self):
        """
        Get local video path upload to azure extract it to frames and metadata, create models and upload it to database.
        :return: server code.
        """
        path = request.json['video_path']
        Logger.logger.info(f'Start to handle path: {path}')

        video_file_name = os.path.basename(path)
        image_list = frame_utils.extract_video_to_frames(path)
        thread_pool = ThreadPoolExecutor(max_workers=3)

        Logger.logger.info(f'Start to upload video for path: {path}')
        upload_video_task = asyncio.create_task(self.azure_container_handler.upload_binary_file(path,
                                                                                                video_file_name,
                                                                                                'videos/'))

        Logger.logger.info(f'Start to upload images for path: {path}')
        self.azure_container_handler.upload_images(image_list, video_file_name, thread_pool)

        Logger.logger.info(f'Start create and insert video frames and metadata to database, video path: {path}')
        video_handle.create_and_insert_to_database_video_metadata_frame_models(path, image_list, video_file_name)

        await upload_video_task
        thread_pool.shutdown(wait=True)

        Logger.logger.info(f'finish to upload video for path: {path}')
        Logger.logger.info(f'finish to upload images for path: {path}')
        Logger.logger.info(f'Finish to insert video and frames to database, video path: {path}')
        Logger.logger.info(f'Finish to handle path: {path}')

        return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}
