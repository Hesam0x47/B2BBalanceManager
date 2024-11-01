#!/usr/bin/env bash
python3 manage.py recreate_database
python3 manage.py migrate
bash scripts/dev/create_superuser.sh