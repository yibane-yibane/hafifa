import sys

from azure.core.exceptions import ResourceExistsError
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from .AzureConfig import AzureConfig


class AzureBlobHandler:
    def __init__(self, container_name='eliya'):
        self.blob_service_client = BlobServiceClient.from_connection_string(AzureConfig.AZURE_CONNECTION_STRING)
        self.container_name = container_name

    def create_container(self):
        try:
            self.blob_service_client.create_container(self.container_name)
        except ResourceExistsError:
            # self.blob_service_client.delete_container(self.container_name)
            pass

    def upload_file(self, file_name, file_data, path):
        blob_client = self.blob_service_client.get_blob_client(container=self.container_name, blob=path+file_name)
        blob_client.upload_blob(file_data, overwrite=True)
