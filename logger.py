import yaml
import logging
import logging.config
from logging import LogRecord

import re

DEFAULT_CONFIG_FILE_PATH = "./logging.yml"

handler = logging.StreamHandler()


class CustomAdapter(logging.LoggerAdapter):
    def __init__(self, logger, extra):
        super(CustomAdapter, self).__init__(logger, extra)
        self.logOrder = 0

    def log(self, level, msg, *args, **kwargs):
        """
        Delegate a log call to the underlying logger, after adding
        contextual information from this adapter instance.
        """
        self.logOrder += 1
        if self.isEnabledFor(level):
            msg, kwargs = self.process(msg, kwargs)
            extra = kwargs.pop("extra")
            if extra is not None:
                extra.update(dict(logOrder=self.logOrder))
            self.logger.log(level, msg, *args, **kwargs, extra=extra)


class MessageTemplateLogRecord(LogRecord):
    # noinspection PyArgumentList
    def __init__(self, name, level, pathname, lineno,
                 msg, args, exc_info, func=None, sinfo=None, **kwargs):
        super(MessageTemplateLogRecord, self).__init__(name, level, pathname, lineno, msg, args,
                                                       exc_info, func, sinfo, **kwargs)
        self.messageTemplate = None

    def getMessage(self):
        """
        Return the message for this LogRecord.

        Return the message for this LogRecord after merging any user-supplied
        arguments with the message.
        """
        msg = str(self.msg)
        if self.args:
            res = re.findall(r'{.*?}', msg)
            if not len(res):
                msg = self.msg % self.args
            else:
                self.messageTemplate = msg
                for i, word in enumerate(res):
                    msg = msg.replace(word, f"{ {i} }")

                msg = msg.format(*self.args)
        return msg


def configure_logger(file_path=None):
    """
    Setup loggers to log the fit way
    :param file_path: path to config file (.yaml)
    """
    if not file_path:
        file_path = DEFAULT_CONFIG_FILE_PATH
    with open(file_path, "rt") as f:
        config = yaml.safe_load(f)

    logging.config.dictConfig(config)
    logging.setLogRecordFactory(MessageTemplateLogRecord)


def init_logger(name, extra=None):

    logger = logging.getLogger(name)
    adapter = CustomAdapter(logger, extra=extra)
    return adapter


