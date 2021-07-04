import os
from hafifa.singleton import Singleton


class AzureConfig(metaclass=Singleton):
    AZURE_CONNECTION_STRING = os.getenv("AZURE_CONNECTION_STRING",
                                        "DefaultEndpointsProtocol=https;AccountName=hafifaos;AccountKey=GYFMpijXyEmd3II\
                                        RPw0DnjH3EhNeUFkSHxtK1i7kiaNdX4vWvf9ijhtE9xGpTZmvPERUygc4N1Elccdf143qWg==;\
                                        EndpointSuffix=core.windows.net")
