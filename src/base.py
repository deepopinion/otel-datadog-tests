import logging

from celery import Celery, signals
from json_log_formatter import VerboseJSONFormatter


app = Celery('ddtrace-tests')


root_logger = logging.getLogger()
root_logger.handlers[0].formatter = VerboseJSONFormatter()


@signals.setup_logging.connect
def on_setup_logging(**kwargs):
    pass
