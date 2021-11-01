# Wrapper for PyGithub package

Build:
```
docker build --no-cache -t pygithub .
```

Run:
```
docker run --rm -it \
  --env-file .env \
  --volume $(pwd)/src:/app \
  pygithub
```
