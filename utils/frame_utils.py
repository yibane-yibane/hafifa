import os
import hafifa.data_base.data_models as data_models
from uuid import uuid4


#get int
def create_frames(images: list, video_id: str, video_name: str):
    return [data_models.Frame(str(uuid4()), video_id, create_frame_os_path(video_name, index), index)
            for index in range(len(images))]


def create_frame_os_path(video_name: str, index: int):
    return os.path.join("frames", video_name, f'frame{index}.jpg')
