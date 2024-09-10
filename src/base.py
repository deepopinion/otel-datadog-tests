import logging
from os import environ
from typing import Any

import orjson
from celery import Celery, signals
from json_log_formatter import VerboseJSONFormatter


app = Celery('ddtrace-tests')


class BaseLogFormatter(VerboseJSONFormatter):
    def to_json(self, record):
        return orjson.dumps(record).decode()

    def json_record(
        self, message: str, extra: dict[str, Any], record: logging.LogRecord
    ) -> dict[str, Any]:
        extra: dict[str, Any] = super().json_record(message, extra, record)

        extra.update({
            "status": extra.pop("levelname"),
            "language": "python",
            "source": "python",
            "span": {
                "kind": "server",
            },
            "logger": {
                "name": extra.pop("name"),
                "thread_name": extra.pop("threadName"),
                "method_name": extra.pop("funcName"),
            },
            "syslog": {
                "timestamp": extra['time'],
            },
            "dd.env": environ["DD_ENV"],
            "dd.service": extra.get("otelServiceName"),
            "dd.trace_id": extra.get("otelTraceID"),
            "dd.span_id": extra.get("otelSpanID"),
        })

        if record.exc_info:
            extra["error"] = {
                "message": record.exc_text,
                "stack": extra.pop("exc_info"),
                "kind": str(record.exc_info),
            }

        return extra


logging.basicConfig(level=logging.INFO)
root_logger = logging.getLogger()
root_logger.handlers[0].formatter = BaseLogFormatter()


@signals.setup_logging.connect
def on_setup_logging(**kwargs):
    pass
