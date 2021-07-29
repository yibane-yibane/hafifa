import json
import os
import asyncio
import hafifa.utils.frame_utils as frame_utils
import hafifa.data_base.DataModelTransactions as DataModelTransactions
from io import BytesIO
from hafifa.singleton import Singleton
from hafifa.logger.logger import Logger
from flask import Flask, request, send_file
from concurrent.futures import ThreadPoolExecutor
from hafifa.flask_app.FlaskConfig import FlaskConfig
from hafifa.object_storage.azure_container_handler import AzureBlobContainerHandler


class FlaskAppHandler(metaclass=Singleton):
    def __init__(self):
        self.app = Flask(__name__, instance_relative_config=False)
        self.app.config.from_object(FlaskConfig)
        self.azure_container_handler = AzureBlobContainerHandler()

    def run(self):
        self.app.add_url_rule('/download_tagged_frames', view_func=self.download_tagged_frames, methods=['POST'])
        self.app.add_url_rule('/video/download/<video_id>',
                              view_func=self.download_video,
                              methods=['GET'])
        self.app.add_url_rule('/frame/path/<video_id>/<index>',
                              view_func=self.get_frame_path_by_index_and_video_id,
                              methods=['GET'])
        self.app.add_url_rule('/frame/paths/<video_id>',
                              view_func=self.get_frames_path_from_video_id,
                              methods=['GET'])
        self.app.add_url_rule('/video/path/<video_id>', view_func=self.get_video_path_by_id, methods=['GET'])
        self.app.add_url_rule('/video/paths', view_func=self.get_videos_paths, methods=['GET'])
        self.app.add_url_rule('/video/upload', view_func=self.upload_video, methods=['POST'])
        self.app.run()

    async def download_tagged_frames(self):
        video_id = request.json['video_id']
        local_path_to_save_frames = request.json['local_path_to_save_frames']

        frames = DataModelTransactions.get_tagged_frame_path_by_video_id(video_id)

        frames_os_path = [frame[0] for frame in frames]

        if not frames_os_path:
            Logger.logger.info(f"Can't find tagged frame for video_id: {video_id}")
        else:
            if not os.path.exists(local_path_to_save_frames):
                os.makedirs(local_path_to_save_frames)

            Logger.logger.info(f"Start downloading frames to local path: {local_path_to_save_frames}")
            for index, path in enumerate(frames_os_path):
                frame_local_path = os.path.join(local_path_to_save_frames, f"frame{index}.png")
                await self.azure_container_handler.save_file_to_local_path(path, frame_local_path)

            Logger.logger.info(f"Finish downloading frames to local path: {local_path_to_save_frames}")

        return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}

    async def download_video(self, video_id):
        video_path = DataModelTransactions.get_video_path_by_id(video_id)

        Logger.logger.info(f'Start to download video id: {video_path}')
        video = await self.azure_container_handler.get_binary_blob_context(video_path)
        Logger.logger.info(f'Finish to download video id: {video_path}')

        return send_file(BytesIO(video), mimetype='video/mp4')

    def get_frame_path_by_index_and_video_id(self, index, video_id):
        frame_path = DataModelTransactions.get_frame_path_by_index_and_video_id(video_id, index)

        return json.dumps({'path': frame_path}), 200, {'ContentType': 'application/json'}

    def get_frames_path_from_video_id(self, video_id):
        frames_paths = DataModelTransactions.get_frames_path_by_video_id(video_id)

        return json.dumps({'frames_paths': frames_paths}), 200, {'ContentType': 'application/json'}

    def get_video_path_by_id(self, video_id):
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
