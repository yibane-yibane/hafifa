import json
import os
import cv2
import asyncio
import hafifa.utils.metadata_utils as metadata_utils
import hafifa.utils.frame_utils as frame_utils
import hafifa.data_base.data_models as data_models
from uuid import uuid4
from flask import Flask, request
from hafifa.singleton import Singleton
from hafifa.logger.logger import Logger
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
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
        self.app.add_url_rule('/get_videos_pathes', view_func=self.get_videos_pathes, methods=['GET'])
        self.app.add_url_rule('/upload_video', view_func=self.upload_video, methods=['POST'])
        self.app.run()

    def get_videos_pathes(self):
        return dict(self.db.get_table_row(data_models.Video, 'os_path'))

    async def upload_video(self):
        """
        Get local video path upload to azure extract it to frames and metadata, create models and upload it to database.
        :return: server code.
        """
        path = request.json['video_path']
        Logger.logger.info(f'Start to handle path: {path}')
        video_file_name = os.path.basename(path)

        Logger.logger.info(f'Start to upload video for path: {path}')

        image_list = metadata_utils.extract_video_to_frames(path)

        Logger.logger.info(f'Start to upload images for path: {path}')
        thread_pool = ThreadPoolExecutor(max_workers=5)
        self.upload_images_to_azure(image_list, video_file_name, thread_pool)

        Logger.logger.info(f'Start create and insert video frames and metadata to database, video path: {path}')
        self.create_and_insert_to_database_video_metadata_frame_models(path, image_list, video_file_name, thread_pool)

        await asyncio.create_task(self.upload_binary_file_to_azure(path, video_file_name, 'videos/'))
        thread_pool.shutdown(wait=True)

        Logger.logger.info(f'finish to upload video for path: {path}')
        Logger.logger.info(f'finish to upload images for path: {path}')
        Logger.logger.info(f'Finish to insert video and frames to database, video path: {path}')
        Logger.logger.info(f'Finish to handle path: {path}')

        return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}

    def create_and_insert_to_database_video_metadata_frame_models(self, path, image_list, video_file_name, thread_pool):
        video_model, metadata_model_list, frame_model_list = self.create_video_metadata_frame_models(path,
                                                                                                     image_list,
                                                                                                     video_file_name)
        thread_pool.submit(self._insert_to_database, video_model, metadata_model_list, frame_model_list)

    def create_video_metadata_frame_models(self, path, image_list, video_file_name):
        """
        Create video metadata and frame db models.
        :param path: Video file path.
        :param image_list: Image list.
        :param video_file_name: Video file name
        :return: video_model, metadata_model_list, frame_model_list.
        """
        video_id = str(uuid4())
        frame_model_list = frame_utils.create_frames(len(image_list), video_id, video_file_name)

        observation = self._get_observation_name_from_path(path)
        video_model = data_models.Video(str(video_id), observation, video_file_name, len(frame_model_list))

        metadata_model_list = self._get_metadata_list_and_set_metadata_for_each_frame(frame_model_list, image_list)

        return video_model, metadata_model_list, frame_model_list

    async def upload_binary_file_to_azure(self, path: str, video_file_name: str, azure_path: str):
        """
        Upload binary file to azure.
        :param path: Local file path.
        :param video_file_name: Video file name.
        :param azure_path: Azure path to upload.
        """
        with open(path, 'rb') as file:
            self.azure_handler.upload_file(video_file_name, file, azure_path)

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

    def _get_observation_name_from_path(self, path: str):
        """
        Extract observation name from path.
        :param path: Video file path.
        :return: Observation name.
        """
        return os.path.basename(path).split('_')[0]

    def _get_metadata_list_and_set_metadata_for_each_frame(self, frames: list, images: list):
        """
        Extract metadata from images, set metadata id for each frame and create metadata instances list.
        :param frames: Frame list.
        :param images: Image list.
        :return: Metadata list.
        """
        metadata_list = list()

        with ProcessPoolExecutor(max_workers=2) as executor:
            for index, image in enumerate(images):
                generate_metadata_process = executor.submit(metadata_utils.generate_metadata, image)
                tag_process = executor.submit(metadata_utils.is_frame_tagged, image)

                fov, azi, lev = generate_metadata_process.result()
                tag = tag_process.result()

                metadata_id = metadata_utils.generate_metadata_id(fov, azi, lev, tag)
                frames[index].set_metadata_id(metadata_id)

                if not metadata_utils.get_metadata_by_id(metadata_list, metadata_id):
                    metadata_list.append(data_models.Metadata(metadata_id, fov, azi, lev, tag))

        return metadata_list

    def _insert_to_database(self, video: data_models.Video, metadata: list, frames: list):
        """
        Insert thr params to database.
        :param video: Video.
        :param metadata: metadata list.
        :param frames: frame list.
        """
        with self.app.app_context():
            self.db.insert_one(video)
            self.db.merge_many(metadata)
            self.db.insert_many(frames)
