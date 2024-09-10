from typing import NoReturn

import patch

import cProfile
import logging
from contextlib import contextmanager
from os import makedirs

from flask_openapi3 import Info, Tag
from flask_openapi3 import OpenAPI
from opentelemetry import trace
from opentelemetry.instrumentation.wsgi import OpenTelemetryMiddleware
from pydantic import BaseModel

from worker import check, chat



info = Info(title="OpenTelemetry Datadog tests", version="0.0.0")
app = OpenAPI(__name__, info=info)
app.wsgi_app = OpenTelemetryMiddleware(app.wsgi_app)
tests_tag = Tag(name="tests", description="Some tests")


logger = logging.getLogger("otel-datadog-tests.nagger")
tracer = trace.get_tracer("otel-datadog-tests.nagger")


class ChatQuery(BaseModel):
    question: str


@contextmanager
def profiling():
    profiler = cProfile.Profile()
    profiler.enable()

    yield

    profiler.disable()
    makedirs("profiling", exist_ok=True)
    profiler.dump_stats("profiling/nag.data")



# @profiling()
def nag():
    logger.info("***** Starting new nag *****")
    with tracer.start_as_current_span("nagging") as span:
        context = span.get_span_context()
        async_task = check.apply_async()
        result = async_task.get()
        logger.info("Got result from worker: %s", result)
        if context.trace_id == result["worker_trace_id"]:
            logger.info("Traces match! :-)")
        else:
            logger.warning("Traces don't match... :-(")
    logger.info("***** Finished nag *****")


@app.get("/nag", summary="Nag Celery", tags=[tests_tag])
def nag_route() -> dict[str, bool]:
    nag()

    return {
        "ok": True,
    }


@app.get("/logs", summary="Check logs", tags=[tests_tag])
def logs_route() -> dict[str, bool]:
    logger.info("This is an info.")
    logger.warning("This is a warning.")
    logger.error("This is an error.")

    return {
        "ok": True,
    }


@app.get("/chat", summary="Chat within Celery", tags=[tests_tag])
def chat_route(query: ChatQuery) -> dict[str, str]:
    async_task = chat.delay(query.question)
    response = async_task.get()

    logger.info("Question: %s / Answer: %s", query.question, response)

    return {
        "answer": response,
    }


@app.get("/crash", summary="Crash hard", tags=[tests_tag])
def crash_route() -> NoReturn:
    raise RuntimeError("Let's crash!")
