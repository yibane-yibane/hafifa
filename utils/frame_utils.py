import os
import cv2
import hafifa.data_base.data_models as data_models


def extract_video_to_frames(path: str):
    vidcap = cv2.VideoCapture(path)
    success, image = vidcap.read()
    frames = []

    while success:
        frames.append(image)  # save frame as JPEG file
        success, image = vidcap.read()

    return frames


def create_frame_models(number_of_frames: int, video_id: str, video_name: str):
    """
    Create frame models without metadata id.
    :param number_of_frames: Number of frames.
    :param video_id: Video id.
    :param video_name: Video name.
    :return: Frame instances list.
    """

    return [data_models.Frame(video_id=video_id, os_path=create_frame_os_path(video_name, index+1), index=index+1)
            for index in range(number_of_frames)]


def create_frame_os_path(video_name: str, index: int):
    return os.path.join("frames", video_name, f'frame{index}.jpg')
