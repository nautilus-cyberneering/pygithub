[![Test workflow for example 01](https://github.com/josecelano/pygithub/actions/workflows/example-01.yml/badge.svg)](https://github.com/josecelano/pygithub/actions/workflows/example-01.yml) [![Test workflow for exmaple 02](https://github.com/josecelano/pygithub/actions/workflows/exmaple-02.yml/badge.svg)](https://github.com/josecelano/pygithub/actions/workflows/exmaple-02.yml) [![Test workflow for exmaple 04](https://github.com/josecelano/pygithub/actions/workflows/exmaple-04.yml/badge.svg)](https://github.com/josecelano/pygithub/actions/workflows/exmaple-04.yml)

## Wrapper for PyGithub package

This repo contains some examples about how to sign commits automatically using GitHub.

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

Run examples:
```
./bin/run-01.sh
./bin/run-04.sh
./bin/run-main.sh
```

> NOTE: running GitHub API examples with your personal token produces not signed commits. The commit is only signe if you use the GITHUB_TOKEN provided to the running workflow.
