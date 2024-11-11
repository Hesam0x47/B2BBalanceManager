#!/bin/bash
set -ex

bash scripts/prepare_db.sh
gunicorn -c gunicorn_config.dev.py