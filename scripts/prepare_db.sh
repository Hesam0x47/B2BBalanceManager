#!/bin/bash

if ! python3 manage.py makemigrations --dry-run --check; then
  echo "Startup Error: We have some unapplied makemigration(s)."
  exit 1
fi

# Check if there are any unapplied migrations
if python3 manage.py showmigrations --plan | grep '\[ \]' > /dev/null; then
    echo "Applying migrations..."
    python3 manage.py migrate
    bash scripts/create_superuser.sh
else
    echo "No migrations to apply."
fi

bash scripts/load_default_data.sh