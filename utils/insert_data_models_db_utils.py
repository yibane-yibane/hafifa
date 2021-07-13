import os

from hafifa.data_base import data_models
from hafifa.data_base.SQLAlchemy import SQLAlchemyHandler
from hafifa.utils import frame_utils, metadata_utils


def create_and_insert_to_database_video_metadata_frame_models(path: str,
                                                              image_list: list,
                                                              video_file_name: str):
    """
    Create and insert to database video metadata and frame models.
    :param path: Video path.
    :param image_list: Image list.
    :param video_file_name: Video file name.
    """
    db = SQLAlchemyHandler()
    observation = get_observation_name_from_path(path)
    video_from_db = db.get_video(observation, video_file_name, len(image_list))

    if not video_from_db:
        db.insert_one(data_models.Video(observation_name=observation, os_path=video_file_name, number_of_frames=len(image_list)))

        video_model = db.get_video(observation_name=observation,
                                   os_path=video_file_name,
                                   number_of_frames=len(image_list))

        frame_model_list = frame_utils.create_frame_models(len(image_list), video_model.id, video_file_name)

        create_and_insert_metadata_and_set_metadata_id_to_frames(frame_model_list, image_list, db)

        db.insert_many(frame_model_list)


def create_and_insert_metadata_and_set_metadata_id_to_frames(frames: list, images: list, db):
    """
    Create and insert metadata and set metadata id to frames.
    :param frames: Frame list.
    :param images: Image list.
    """
    for index, image in enumerate(images):
        fov, azi, elev, tag = metadata_utils.get_metadata_arguments(image)
        metadata = db.get_metadata(fov, azi, elev, tag)

        if not metadata:
            db.insert_one(data_models.Metadata(fov=fov, azimuth=azi, elevation=elev, tag=tag))
            metadata = db.get_metadata(fov, azi, elev, tag)

        frames[index].set_metadata_id(metadata.id)


def get_observation_name_from_path(path: str):
    """
    Extract observation name from path.
    :param path: Video file path.
    :return: Observation name.
    """
    return os.path.basename(path).split('_')[0]
