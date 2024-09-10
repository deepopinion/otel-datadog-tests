#!/usr/bin/env just --justfile

set dotenv-load

build:
  docker compose pull
  docker compose build

run:
  docker compose up

print-otel-requirements:
  poetry run opentelemetry-bootstrap -a requirements
