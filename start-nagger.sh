#!/usr/bin/env bash

export OTEL_SERVICE_NAME=nagger

poetry run opentelemetry-instrument gunicorn -c gunicorn.conf.py nagger:app
