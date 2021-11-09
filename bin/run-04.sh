#!/bin/bash

docker run --rm -it \
  --env-file .env \
  --env INPUT_BRANCH=main \
  --volume $(pwd):/app \
  pygithub python src/04_sign_commit_with_multiple_files_using_github_api.py