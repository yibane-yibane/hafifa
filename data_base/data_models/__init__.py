from hafifa.data_base.data_models.Frame import Frame
from hafifa.data_base.data_models.Video import Video
from hafifa.data_base.data_models.Metadata import Metadata

DATA_MODEL_TYPES = {
    "FRAME": "Frame",
    "VIDEO": "Video",
    "METADATA": "Metadata"
}


def data_models_factory(data_model, args):
    if DATA_MODEL_TYPES["FRAME"] == data_model:
        return Frame(args[0], args[1], args[2], args[3], args[4])
    elif DATA_MODEL_TYPES["VIDEO"] == data_model:
        return Video(args[0], args[1], args[2], args[3])
    elif DATA_MODEL_TYPES["METADATA"] == data_model:
        return Metadata(args[0], args[1], args[2], args[3], args[4])
