import logging
import sys

from hafifa.singleton import Singleton


class Logger(metaclass=Singleton):
    logger = logging.getLogger()
    # logger.setLevel(logging.INFO)
    # formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s',
    #                               '%m-%d-%Y %H:%M:%S')
    #
    # stdout_handler = logging.StreamHandler(sys.stdout)
    # stdout_handler.setLevel(logging.DEBUG)
    # stdout_handler.setFormatter(formatter)
    #
    # logger.addHandler(stdout_handler)
