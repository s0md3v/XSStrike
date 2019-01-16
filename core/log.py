import logging
from .colors import *

__all__ = ['setup_logger', 'console_log_level', 'file_log_level', 'log_file']

console_log_level = 'INFO'
file_log_level = None
log_file = 'xsstrike.log'

"""
Default Logging Levels
CRITICAL = 50
ERROR = 40
WARNING = 30
INFO = 20
DEBUG = 10
"""

VULN_LEVEL_NUM = 60
RUN_LEVEL_NUM = 22
GOOD_LEVEL_NUM = 25


logging.addLevelName(VULN_LEVEL_NUM, 'VULN')
logging.addLevelName(RUN_LEVEL_NUM, 'RUN')
logging.addLevelName(GOOD_LEVEL_NUM, 'GOOD')


def _vuln(self, msg, *args, **kwargs):
    if self.isEnabledFor(VULN_LEVEL_NUM):
        self._log(VULN_LEVEL_NUM, msg, args, **kwargs)


def _run(self, msg, *args, **kwargs):
    if self.isEnabledFor(RUN_LEVEL_NUM):
        self._log(RUN_LEVEL_NUM, msg, args, **kwargs)


def _good(self, msg, *args, **kwargs):
    if self.isEnabledFor(GOOD_LEVEL_NUM):
        self._log(GOOD_LEVEL_NUM, msg, args, **kwargs)


logging.Logger.vuln = _vuln
logging.Logger.run = _run
logging.Logger.good = _good


log_config = {
    'DEBUG': {
        'value': logging.DEBUG,
        'prefix': '{}[*]{}'.format(yellow, end),
    },
    'INFO': {
        'value': logging.INFO,
        'prefix': info,
    },
    'RUN': {
        'value': RUN_LEVEL_NUM,
        'prefix': run,
    },
    'GOOD': {
        'value': GOOD_LEVEL_NUM,
        'prefix': good,
    },
    'WARNING': {
        'value': logging.WARNING,
        'prefix': '[!!]'.format(yellow, end),
    },
    'ERROR': {
        'value': logging.ERROR,
        'prefix': bad,
    },
    'CRITICAL': {
        'value': logging.CRITICAL,
        'prefix': '{}[--]{}'.format(red, end),
    },
    'VULN': {
        'value': VULN_LEVEL_NUM,
        'prefix': '{}[++]{}'.format(green, red),
    }
}


class CustomFormatter(logging.Formatter):
    def format(self, record):
        msg = super().format(record)
        if record.levelname in log_config.keys():
            msg = '%s %s %s' % (log_config[record.levelname]['prefix'], msg, end)
        return msg


class CustomStreamHandler(logging.StreamHandler):
    default_terminator = '\n'

    def emit(self, record):
        """
        Overrides emit method to temporally update terminator character in case last log record character is '\r'
        :param record:
        :return:
        """
        if record.msg.endswith('\r'):
            self.terminator = '\r'
            super().emit(record)
            self.terminator = self.default_terminator
        else:
            super().emit(record)


def _switch_to_no_format_loggers(self):
    self.removeHandler(self.console_handler)
    self.addHandler(self.no_format_console_handler)
    if hasattr(self, 'file_handler') and hasattr(self, 'no_format_file_handler'):
        self.removeHandler(self.file_handler)
        self.addHandler(self.no_format_file_handler)


def _switch_to_default_loggers(self):
    self.removeHandler(self.no_format_console_handler)
    self.addHandler(self.console_handler)
    if hasattr(self, 'file_handler') and hasattr(self, 'no_format_file_handler'):
        self.removeHandler(self.no_format_file_handler)
        self.addHandler(self.file_handler)


def _get_level_and_log(self, msg, level):
    if level.upper() in log_config.keys():
        log_method = getattr(self, level.lower())
        log_method(msg)
    else:
        self.info(msg)


def log_red_line(self, amount=60, level='INFO'):
    _switch_to_no_format_loggers(self)
    _get_level_and_log(self, red + ('-' * amount) + end, level)
    _switch_to_default_loggers(self)


def log_no_format(self, msg='', level='INFO'):
    _switch_to_no_format_loggers(self)
    _get_level_and_log(self, msg, level)
    _switch_to_default_loggers(self)


def log_debug_json(self, msg='', data={}):
    if self.isEnabledFor(logging.DEBUG):
        if isinstance(data, dict):
            import json
            try:
                self.debug('{} {}'.format(msg, json.dumps(data, indent=2)))
            except TypeError:
                self.debug('{} {}'.format(msg, data))
        else:
            self.debug('{} {}'.format(msg, data))


def setup_logger(name='xsstrike'):
    from types import MethodType
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    console_handler = CustomStreamHandler(sys.stdout)
    console_handler.setLevel(log_config[console_log_level]['value'])
    console_handler.setFormatter(CustomFormatter('%(message)s'))
    logger.addHandler(console_handler)
    # Setup blank handler to temporally use to log without format
    no_format_console_handler = CustomStreamHandler(sys.stdout)
    no_format_console_handler.setLevel((log_config[console_log_level]['value']))
    no_format_console_handler.setFormatter(logging.Formatter(fmt=''))
    # Store current handlers
    logger.console_handler = console_handler
    logger.no_format_console_handler = no_format_console_handler

    if file_log_level:
        detailed_formatter = logging.Formatter('%(asctime)s %(name)s - %(levelname)s - %(message)s')
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_config[file_log_level]['value'])
        file_handler.setFormatter(detailed_formatter)
        logger.addHandler(file_handler)
        # Setup blank handler to temporally use to log without format
        no_format_file_handler = logging.FileHandler(log_file)
        no_format_file_handler.setLevel(log_config[file_log_level]['value'])
        no_format_file_handler.setFormatter(logging.Formatter(fmt=''))
        # Store file handlers
        logger.file_handler = file_handler
        logger.no_format_file_handler = no_format_file_handler

    # Create logger method to only log a red line
    logger.red_line = MethodType(log_red_line, logger)
    # Create logger method to log without format
    logger.no_format = MethodType(log_no_format, logger)
    # Create logger method to convert data to json and log with debug level
    logger.debug_json = MethodType(log_debug_json, logger)
    return logger
