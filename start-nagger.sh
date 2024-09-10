#!/usr/bin/env bash

poetry run gunicorn -c gunicorn.conf.py nagger:app
