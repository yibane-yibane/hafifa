import os
import cv2
from hafifa.logger.logger import Logger
from azure.storage.blob import ContainerClient
from azure.core.exceptions import ResourceExistsError
from concurrent.futures.thread import ThreadPoolExecutor


class AzureBlobContainerHandler:
    def __init__(self, container_name='eliya'):
        self.blob_container_client = ContainerClient.from_connection_string(os.getenv("AZURE_CONNECTION_STRING"),
                                                                            container_name=container_name)
        self.create_container_client()

    def create_container_client(self):
        try:
            self.blob_container_client.create_container()
        except ResourceExistsError:
            Logger.logger.info("container already exists")

    def upload_file(self, file_name: str, file_data: bytes, path: str):
        blob_client = self.blob_container_client.get_blob_client(blob=path+file_name)
        blob_client.upload_blob(file_data, overwrite=True)

    def upload_images(self, images: list, video_file_name: str, thread_pool: ThreadPoolExecutor):
        """
        Upload images to azure in background with thread pool
        :param images: List of images
        :param video_file_name: Video file name
        :param thread_pool: Thread pool
        """
        for index, image in enumerate(images):
            _, img_encode = cv2.imencode('.jpg', image)
            img_bytes = img_encode.tobytes()
            thread_pool.submit(self.upload_file, f'frame{index}.jpg',
                               img_bytes, os.path.join('frames', video_file_name))

    async def upload_binary_file(self, path: str, file_name: str, azure_path: str):
        """
        Upload binary file to azure.
        :param path: Local file path.
        :param file_name: File name.
        :param azure_path: Azure path to upload.
        """
        with open(path, 'rb') as file:
            self.upload_file(file_name, file, azure_path)
