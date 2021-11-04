#!/bin/bash

docker run --rm -it \
  --env-file .env \
  --volume $(pwd):/app \
  pygithub python src/01_sign_commit_using_github_api.py