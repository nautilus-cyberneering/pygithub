#!/bin/bash

docker run --rm -it \
  --volume $(pwd):/app \
  pygithub src/05_commit_using_the_gitpython_package_without_signing.py