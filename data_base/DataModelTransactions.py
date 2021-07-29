import os
from hafifa.data_base import data_models
from hafifa.data_base.SQLAlchemy import SQLAlchemyHandler
from hafifa.logger.logger import Logger
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
    observation = metadata_utils.get_observation_name_from_path(path)
    is_video_exists = db.is_data_model_exists(data_model=data_models.Video,
                                              where_section={'observation_name': observation,
                                                             'os_path': os.path.join('videos', video_file_name),
                                                             'number_of_frames': len(image_list)})

    if not is_video_exists:
        Logger.logger.info('Start create and insert video frames and metadata to database, video path: '
                           f'{path}')
        video_model = data_models.Video(observation_name=observation,
                                        os_path=os.path.join('videos', video_file_name),
                                        number_of_frames=len(image_list))

        db.insert_one(video_model)

        frame_model_list = frame_utils.create_frame_models(len(image_list), video_model.id, video_file_name)

        create_and_insert_metadata_and_set_metadata_id_to_frames(frame_model_list, image_list)

        db.insert_many(frame_model_list)

        Logger.logger.info('Finish create and insert video frames and metadata to database, video path: '
                           f'{path}')


def create_and_insert_metadata_and_set_metadata_id_to_frames(frames: list, images: list):
    """
    Create and insert metadata and set metadata id to frames.
    :param frames: Frame list.
    :param images: Image list.
    """
    db = SQLAlchemyHandler()
    for index, image in enumerate(images):
        fov, azi, elev, tag = metadata_utils.get_metadata_arguments(image)
        metadata = db.get_entities(select_section=[getattr(data_models.Metadata, 'id')],
                                   attributes_filters={getattr(data_models.Metadata, 'fov'): fov,
                                                       getattr(data_models.Metadata, 'azimuth'): azi,
                                                       getattr(data_models.Metadata, 'elevation'): elev,
                                                       getattr(data_models.Metadata, 'tag'): tag},
                                   count=1)

        if metadata is None:
            metadata = data_models.Metadata(fov=fov, azimuth=azi, elevation=elev, tag=tag)
            db.insert_one(metadata)

        frames[index].set_metadata_id(metadata.id)


def get_videos_paths():
    db = SQLAlchemyHandler()
    return db.get_entities(select_section=[getattr(data_models.Video, 'os_path')],
                           attributes_filters={})


def get_video_path_by_id(video_id):
    db = SQLAlchemyHandler()

    # Returns tuple so need to extract the path from it
    return db.get_entities(select_section=[getattr(data_models.Video, 'os_path')],
                           attributes_filters={getattr(data_models.Video, 'id'): video_id},
                           count=1)[0]


def get_frames_path_by_video_id(video_id):
    db = SQLAlchemyHandler()
    return db.get_entities(select_section=[getattr(data_models.Frame, 'os_path')],
                           attributes_filters={getattr(data_models.Frame, 'video_id'): video_id})


def get_frame_path_by_index_and_video_id(video_id, frame_index):
    db = SQLAlchemyHandler()
    return db.get_entities(select_section=[getattr(data_models.Frame, 'os_path')],
                           attributes_filters={getattr(data_models.Frame, 'video_id'): video_id,
                                               getattr(data_models.Frame, 'index'): frame_index})


def get_tagged_frame_path_by_video_id(video_id):
    db = SQLAlchemyHandler()
    db.get_entities(select_section=[getattr(data_models.Frame, 'os_path')],
                    attributes_filters={getattr(data_models.Frame, 'video_id'): video_id,
                                        getattr(data_models.Frame, 'metadata_id'): data_models.Metadata.id,
                                        getattr(data_models.Metadata, 'tag'): True})
