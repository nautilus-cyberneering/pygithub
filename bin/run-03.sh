#!/bin/bash

docker run --rm -it \
  --env-file .env \
  --env INPUT_MODE=test \
  --env INPUT_REPO_DIR=/app \
  --volume $(pwd):/app \
  pygithub src/03_sign_commit_using_the_gitpython_package.py