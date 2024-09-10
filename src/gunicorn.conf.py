from os import environ


def post_fork(server, worker):
    server.log.info("Worker spawned (pid: %s)", worker.pid)

    # _setup_opentelemetry()


def _setup_opentelemetry():
    from opentelemetry import trace
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import \
        OTLPSpanExporter
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor

    resource = Resource.create(attributes={
        "service.name": "api-service"
    })
    trace.set_tracer_provider(TracerProvider(resource=resource))
    span_processor = BatchSpanProcessor(
        OTLPSpanExporter(
            endpoint=environ["OTEL_EXPORTER_OTLP_TRACES_ENDPOINT"]
        )
    )
    trace.get_tracer_provider().add_span_processor(span_processor)


worker_class = "gevent"
workers = 1
bind = ["0.0.0.0:8000"]
