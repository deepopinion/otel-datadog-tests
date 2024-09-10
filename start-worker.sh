#!/usr/bin/env bash

poetry run opentelemetry-instrument celery -A worker worker --loglevel="${LOG_LEVEL}" --concurrency=1 -n worker1
