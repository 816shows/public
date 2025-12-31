#!/bin/bash

# Explicitly set the HOME environment variable for Firefox profiles
# This is still important for Firefox to have a writable directory for its profile.
export HOME="/tmp"

# Execute the original Lambda entrypoint with the provided arguments
/lambda-entrypoint.sh "$@"