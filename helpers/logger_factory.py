from pathlib import Path
import logging
import os
from os.path import basename, dirname
import config

_plugin_name = basename(Path(dirname(__file__)).parent)

def __build_plugin_logger() -> logging.Logger:
    logger_name = f'{config.appname}.{_plugin_name}'
    _logger = logging.getLogger(logger_name)

    if not _logger.hasHandlers():
        _logger.setLevel(logging.INFO)
        logger_channel = logging.StreamHandler()
        logger_formatter = logging.Formatter(f'%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(lineno)d:%(funcName)s: %(message)s')
        logger_formatter.default_time_format = '%Y-%m-%d %H:%M:%S'
        logger_formatter.default_msec_format = '%s.%03d'
        logger_channel.setFormatter(logger_formatter)
        _logger.addHandler(logger_channel)

    return _logger

logger = __build_plugin_logger()
