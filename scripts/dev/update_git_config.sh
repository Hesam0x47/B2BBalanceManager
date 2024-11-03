#!/usr/bin/env bash

# Add shared .gitconfig settings to local Git configuration
# This command will ensure the local repository configuration (.git/config) includes the settings from shared.gitconfig.
git config --local include.path ../shared.gitconfig
echo "Applied shared git configuration."
