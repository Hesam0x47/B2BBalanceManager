#!/bin/bash

set -ex

python3 manage.py loaddata default_data.json
