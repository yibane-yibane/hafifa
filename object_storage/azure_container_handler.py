import os
import cv2
from hafifa.logger.logger import Logger
from azure.storage.blob import ContainerClient
from azure.storage.blob.aio import ContainerClient as ContainerClientAsync
from azure.core.exceptions import ResourceExistsError
from concurrent.futures.thread import ThreadPoolExecutor


class AzureBlobContainerHandler:
    def __init__(self, container_name='eliya'):
        self.blob_container_client_async = \
            ContainerClientAsync.from_connection_string(os.getenv("AZURE_CONNECTION_STRING"),
                                                        container_name=container_name)
        self.blob_container_client = \
            ContainerClient.from_connection_string(os.getenv("AZURE_CONNECTION_STRING"),
                                                   container_name=container_name)
        self.create_container_client()

    def create_container_client(self):
        try:
            self.blob_container_client.create_container()
        except ResourceExistsError:
            Logger.logger.info("container already exists")

    def upload_images(self, images: list, azure_path: str, thread_pool: ThreadPoolExecutor, local_file_path: str):
        """
        Upload images to azure.
        :param images: List of images.
        :param azure_path: Path in azure.
        :param thread_pool: Thread pool.
        :param local_file_path:
        """
        Logger.logger.info(f'Start to upload images for path: {local_file_path}')

        for index, image in enumerate(images):
            _, img_encode = cv2.imencode('.jpg', image)
            img_bytes = img_encode.tobytes()
            thread_pool.submit(self.upload_blob, img_bytes, os.path.join(azure_path, f'frame{index+1}.jpg'))

        Logger.logger.info(f'Finish to upload images for path: {local_file_path}')

    def upload_blob(self, data: bytes, azure_path: str):
        """
        Upload a file azure.
        :param data: File data to upload.
        :param azure_path: Azure path.
        """
        blob_client = self.blob_container_client.get_blob_client(blob=azure_path)
        blob_client.upload_blob(data, overwrite=True)

    async def upload_binary_file(self, local_file_path: str, azure_path: str):
        """
        Upload binary file to azure.
        :param local_file_path: Local file path.
        :param azure_path: Azure path to upload.
        """
        Logger.logger.info(f'Start to upload file for path: {local_file_path}')

        with open(local_file_path, 'rb') as file:
            blob_client = self.blob_container_client_async.get_blob_client(blob=azure_path)
            await blob_client.upload_blob(file, blob_type="BlockBlob", overwrite=True)
            Logger.logger.info(f'Finish to upload video for path: {local_file_path}')

    async def save_file_to_local(self, os_path: str, local_path: str):
        blob = await self.blob_container_client_async.download_blob(blob=os_path)

        Logger.logger.info(f'Start to download file to: {local_path}')
        with open(local_path, 'wb+') as file:
            bytes = await blob.readall()
            file.write(bytes)

        Logger.logger.info(f'Finish to download file to: {local_path}')
