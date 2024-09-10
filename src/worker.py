import logging
import time

from opentelemetry import trace

from base import app


logger = logging.getLogger("otel-datadog-tests.worker")
tracer = trace.get_tracer("otel-datadog-tests.nagger")


@app.task(bind=True)
def check(self):
    time.sleep(0.1)
    logger.info("Bound headers: %s", self.request.headers)
    with tracer.start_as_current_span("checking") as span:
        context = span.get_span_context()
        logger.info(
            "Worker got trace ID %s, span ID %s",
            context.trace_id, context.span_id
        )
        logging.getLogger().handlers[0].flush()
        time.sleep(1)
        return {
            "worker_trace_id": context.trace_id,
            "worker_span_id": context.span_id,
        }
