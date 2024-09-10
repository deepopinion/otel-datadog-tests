import patch
import cProfile
import logging
from contextlib import contextmanager
from os import makedirs

from flask import Flask
from opentelemetry import trace
from opentelemetry.instrumentation.wsgi import OpenTelemetryMiddleware

from worker import check

app = Flask(__name__)
app.wsgi_app = OpenTelemetryMiddleware(app.wsgi_app)


logger = logging.getLogger("otel-datadog-tests.nagger")
tracer = trace.get_tracer("otel-datadog-tests.nagger")


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
        logger.info(
            "Nagger got trace ID %s, span ID %s",
            context.trace_id, context.span_id
        )
        if context.trace_id == result["worker_trace_id"]:
            logger.info("Traces match! :-)")
        else:
            logger.warning("Traces don't match... :-(")
        if context.span_id == result["worker_span_id"]:
            logger.info("Spans match! :-)")
        else:
            logger.warning("Spans don't match... :-(")
    logger.info("***** Finished nag *****")


@app.route("/")
def home():
    nag()

    return "Done!"
