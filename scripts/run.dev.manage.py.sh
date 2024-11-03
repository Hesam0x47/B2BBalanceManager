#!/bin/bash
set -ex

bash scripts/prepare_db.sh
python3 manage.py runserver 0.0.0.0:8000