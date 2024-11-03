#!/bin/bash
### RUN THIS SCRIPT USING `source apply_dot_env_file.sh` ###

export $(grep -v '^#' .env.dev.ide | xargs)
