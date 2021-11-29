#!/bin/bash

docker run --rm -it \
  --env-file .env \
  --env MODE=test \
  --env REPO_DIR=/app \
  --volume "$(pwd):/app" \
  pygithub src/03_sign_commit_using_the_gitpython_package.py