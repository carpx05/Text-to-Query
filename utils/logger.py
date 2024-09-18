from enum import Enum


class LogType(Enum):
    """
    Enum class for log types.
    """

    INFO = "info"
    DEBUG = "debug"
    ERROR = "error"
    WARNING = "warning"


def log(tag, message_type, message):
    """
    Logs a message with the specified tag and message type.
    """

    if message_type == LogType.DEBUG:
        print("[Debug] " + tag + " : " + str(message))
    elif message_type == LogType.ERROR:
        print("[Error] " + tag + " : " + str(message))
    elif message_type == LogType.WARNING:
        print("[Warning] " + tag + " : " + str(message))
    else:
        print("[Info] " + tag + " : " + str(message))