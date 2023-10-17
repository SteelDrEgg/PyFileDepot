import logging.config
from enum import Enum


class level(Enum):
    DEBUG: str = "DEBUG"
    INFO: str = "INFO"
    WARNING: str = "WARNING"
    ERROR: str = "ERROR"
    CRITICAL: str = "CRITICAL"


def configLoggin(logLevel: level, logFile=None):
    LOGGING_CONFIG = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'my_formatter': {
                'format': '[%(levelname)s] <%(asctime)s> %(message)s ',
                'datefmt': "%Y-%m-%d %H:%M:%S"
            },
        },
        'handlers': {
            'stream_handler': {
                'class': 'logging.StreamHandler',
                'formatter': 'my_formatter',
            },
        },
        'loggers': {
            'mainLogger': {
                'handlers': ['stream_handler'],
                'level': logLevel.value if isinstance(logLevel, level) else logLevel,
                'propagate': True,
            }
        }
    }
    if logFile:
        LOGGING_CONFIG["handlers"]["file_handler"] = {
            'class': 'logging.FileHandler',
            'filename': f'{logFile}',
            'formatter': 'my_formatter',
        }
        "file_handler"
        LOGGING_CONFIG["loggers"]["mainLogger"]["handlers"].append("file_handler")
    logging.config.dictConfig(LOGGING_CONFIG)
