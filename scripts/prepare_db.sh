#!/bin/bash

if ! python3 manage.py makemigrations --dry-run --check; then
  echo "Startup Error: We have some unapplied migration(s)."
  exit 1
fi

python3 manage.py migrate

