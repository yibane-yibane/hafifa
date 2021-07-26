import json
import os
import asyncio
import hafifa.utils.frame_utils as frame_utils
import hafifa.data_base.DataModelTransactions as DataModelTransactions
from flask import Flask, request
from hafifa.singleton import Singleton
from hafifa.logger.logger import Logger
from concurrent.futures import ThreadPoolExecutor
from hafifa.flask_app.FlaskConfig import FlaskConfig
from hafifa.object_storage.azure_container_handler import AzureBlobContainerHandler


class FlaskAppHandler(metaclass=Singleton):
    def __init__(self):
        self.app = Flask(__name__, instance_relative_config=False)
        self.app.config.from_object(FlaskConfig)
        self.azure_container_handler = AzureBlobContainerHandler()

    def run(self):
        self.app.add_url_rule('/frame_path_by_index_and_videoid',
                              view_func=self.get_frame_path_by_index_and_video_id,
                              methods=['POST'])
        self.app.add_url_rule('/frames_path_by_videoid', view_func=self.get_frames_path_from_video_id, methods=['POST'])
        self.app.add_url_rule('/video_path_by_id', view_func=self.get_video_path_by_id, methods=['POST'])
        self.app.add_url_rule('/get_videos_paths', view_func=self.get_videos_paths, methods=['GET'])
        self.app.add_url_rule('/upload_video', view_func=self.upload_video, methods=['POST'])
        self.app.run()

    def get_frame_path_by_index_and_video_id(self):
        video_id = request.json['video_id']
        frame_index = request.json['frame_index']
        videos_dict = dict(DataModelTransactions.get_frame_path_by_index_and_video_id(video_id, frame_index))

        return json.dumps({'path': videos_dict}), 200, {'ContentType': 'application/json'}

    def get_frames_path_from_video_id(self):
        video_id = request.json['video_id']
        frames_paths = DataModelTransactions.get_frames_path_by_video_id(video_id)

        return json.dumps({'frames_paths': frames_paths}), 200, {'ContentType': 'application/json'}

    def get_video_path_by_id(self):
        video_id = request.json['video_id']
        video_path = DataModelTransactions.get_video_path_by_id(video_id)

        return json.dumps({'path': video_path}), 200, {'ContentType': 'application/json'}

    def get_videos_paths(self):
        videos_paths = DataModelTransactions.get_videos_paths()
        return json.dumps({'videos_paths': videos_paths}), 200, {'ContentType': 'application/json'}

    async def upload_video(self):
        """
        Get local video path upload to azure extract it to frames and metadata, create models and upload it to database.
        :return: server code.
        """
        local_video_path = request.json['video_path']
        Logger.logger.info(f'Start to handle path: {local_video_path}')

        video_file_name = os.path.basename(local_video_path)
        image_list = frame_utils.extract_video_to_frames(local_video_path)
        thread_pool = ThreadPoolExecutor(max_workers=3)

        upload_video_task = asyncio.create_task(
            self.azure_container_handler.upload_binary_file(local_video_path,
                                                            os.path.join('videos', video_file_name)))

        self.azure_container_handler.upload_images(image_list,
                                                   os.path.join('frames', video_file_name),
                                                   thread_pool,
                                                   local_video_path)

        DataModelTransactions.create_and_insert_to_database_video_metadata_frame_models(local_video_path,
                                                                                        image_list,
                                                                                        video_file_name)

        await upload_video_task
        thread_pool.shutdown(wait=True)

        Logger.logger.info(f'Finish to handle path: {local_video_path}')

        return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}
