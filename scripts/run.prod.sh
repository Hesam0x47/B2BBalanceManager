#!/bin/bash

bash scripts/prepare_db.sh
gunicorn -c gunicorn_config.py