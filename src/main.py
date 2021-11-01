import base64
import os
from pprint import pprint

from git import Repo
from github import Github


def main(repo_token):
    gh = Github(repo_token)

    repository = "josecelano/mandelbrot-explorer"

    repo = gh.get_repo(repository)

    commit = repo.get_commit("0dd65f3241250afa591b4ef1d99eec92a59352e5")

    pprint(commit)

    issue = repo.get_issue(number=1)

    pprint(issue)

if __name__ == "__main__":
    # https://pygithub.readthedocs.io
    repo_token = os.environ["INPUT_REPO_TOKEN"]
    main(repo_token)
