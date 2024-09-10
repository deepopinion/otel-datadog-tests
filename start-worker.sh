#!/usr/bin/env bash

export OTEL_SERVICE_NAME=worker

poetry run opentelemetry-instrument celery -A worker worker --loglevel="${LOG_LEVEL}" --concurrency=1 -n worker1
