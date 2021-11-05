[![Test workflow for sample 01](https://github.com/josecelano/pygithub/actions/workflows/sample-01.yml/badge.svg)](https://github.com/josecelano/pygithub/actions/workflows/sample-01.yml) [![Test workflow for sample 02](https://github.com/josecelano/pygithub/actions/workflows/sample-02.yml/badge.svg)](https://github.com/josecelano/pygithub/actions/workflows/sample-02.yml)

## Wrapper for PyGithub package

This repo is a sample repo containing some examples about how to sign commits automatically using GitHub.

You can read the full article [here](docs/how_to_sign_automatic_commits_in_github_actions.md).

## Build and run

Build docker image:
```
./bin/build.sh
```

Run all examples in `src/main.py`:
```
./bin/run-main.sh
```

Run a given example:
```
./bin/run-01.sh
./bin/run-XX.sh
```
