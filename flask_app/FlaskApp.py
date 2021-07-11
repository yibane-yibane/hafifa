import json
import os
import cv2
import asyncio
import hafifa.utils.metadata_utils as metadata_utils
import hafifa.utils.frame_utils as frame_utils
import hafifa.data_base.data_models as data_models
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
        image_list = metadata_utils.extract_video_to_frames(path)
        thread_pool = ThreadPoolExecutor(max_workers=3)

        Logger.logger.info(f'Start to upload video for path: {path}')
        upload_video_task = asyncio.create_task(self.upload_binary_file_to_azure(path, video_file_name, 'videos/'))

        Logger.logger.info(f'Start to upload images for path: {path}')
        self.upload_images_to_azure(image_list, video_file_name, thread_pool)

        Logger.logger.info(f'Start create and insert video frames and metadata to database, video path: {path}')
        self.create_and_insert_to_database_video_metadata_frame_models(path, image_list, video_file_name)

        await upload_video_task
        thread_pool.shutdown(wait=True)

        Logger.logger.info(f'finish to upload video for path: {path}')
        Logger.logger.info(f'finish to upload images for path: {path}')
        Logger.logger.info(f'Finish to insert video and frames to database, video path: {path}')
        Logger.logger.info(f'Finish to handle path: {path}')

        return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}

    def upload_images_to_azure(self, images: list, video_file_name: str, thread_pool: ThreadPoolExecutor):
        """
        Upload images to azure in background with thread pool
        :param images: List of images
        :param video_file_name: Video file name
        :param thread_pool: Thread pool
        """
        for index, image in enumerate(images):
            _, img_encode = cv2.imencode('.jpg', image)
            img_bytes = img_encode.tobytes()
            thread_pool.submit(self.azure_handler.upload_file, f'frame{index}.jpg',
                               img_bytes, os.path.join('frames', video_file_name))

    def create_and_insert_to_database_video_metadata_frame_models(self,
                                                                  path: str,
                                                                  image_list: list,
                                                                  video_file_name: str):
        """
        Create and insert to database video metadata and frame models.
        :param path: Video path.
        :param image_list: Image list.
        :param video_file_name: Video file name.
        """
        observation = self._get_observation_name_from_path(path)
        video_from_db = self.db.get_video(observation, video_file_name, len(image_list))

        if not video_from_db:
            self.db.insert_one(data_models.Video(observation_name=observation,
                                                 os_path=video_file_name,
                                                 number_of_frames=len(image_list)))

            video_model = self.db.get_video(observation_name=observation,
                                            os_path=video_file_name,
                                            number_of_frames=len(image_list))

            frame_model_list = frame_utils.create_frame_models(len(image_list), video_model.id, video_file_name)

            self.create_and_insert_metadata_and_set_metadata_id_to_frames(frame_model_list, image_list)

            self.db.insert_many(frame_model_list)

    def _get_observation_name_from_path(self, path: str):
        """
        Extract observation name from path.
        :param path: Video file path.
        :return: Observation name.
        """
        return os.path.basename(path).split('_')[0]

    def create_and_insert_metadata_and_set_metadata_id_to_frames(self, frames: list, images: list):
        """
        Create and insert metadata and set metadata id to frames.
        :param frames: Frame list.
        :param images: Image list.
        """
        for index, image in enumerate(images):
            fov, azi, elev, tag = self.get_metadata_arguments(image)
            metadata = self.db.get_metadata(fov, azi, elev, tag)

            if not metadata:
                self.db.insert_one(data_models.Metadata(fov=fov, azimuth=azi, elevation=elev, tag=tag))
                metadata = self.db.get_metadata(fov, azi, elev, tag)

            frames[index].set_metadata_id(metadata.id)

    def get_metadata_arguments(self, image: list):
        """
        Extract fov, azi, elev, tag parameters from image.
        :param image: Image.
        :return: fov, azi, elev, tag
        """
        fov, azi, elev = metadata_utils.generate_metadata(image)
        tag = metadata_utils.is_frame_tagged(image)

        return fov, azi, elev, tag

    async def upload_binary_file_to_azure(self, path: str, video_file_name: str, azure_path: str):
        """
        Upload binary file to azure.
        :param path: Local file path.
        :param video_file_name: Video file name.
        :param azure_path: Azure path to upload.
        """
        with open(path, 'rb') as file:
            self.azure_handler.upload_file(video_file_name, file, azure_path)
