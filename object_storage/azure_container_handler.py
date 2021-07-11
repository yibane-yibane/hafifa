import os
from hafifa.logger.logger import Logger
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceExistsError


class AzureBlobContainerHandler:
    def __init__(self, container_name='eliya'):
        self.blob_service_client = BlobServiceClient.from_connection_string(os.getenv("AZURE_CONNECTION_STRING"))
        self.container_name = container_name

    def create_container(self):
        try:
            self.blob_service_client.create_container(self.container_name)
        except ResourceExistsError:
            Logger.logger.info(f"The container: {self.container_name} already exists")
            pass

    def upload_file(self, file_name: str, file_data: bytes, path: str):
        blob_client = self.blob_service_client.get_blob_client(container=self.container_name, blob=path+file_name)
        blob_client.upload_blob(file_data, overwrite=True)
