#!/bin/bash

docker run --rm -it \
  --env-file .env \
  --volume $(pwd):/app \
  pygithub