import base64
import hashlib
import os
from pprint import pprint

from git import Repo
from github import Github


def main(repo_token):
    gh = Github(repo_token)

    repository = "Nautilus-Cyberneering/chinese-ideographs-website"

    remote_repo = gh.get_repo(repository)

    commit = remote_repo.get_commit("79c3511c1eba9329665dc64c1bd55ff4cffeb98b")

    pprint(commit)

    issue = remote_repo.get_issue(number=1)

    pprint(issue)

    # 1 MB limit
    issue = remote_repo.get_contents(
        "public/images/.gitkeep", "issue-1-import-base-images")

    local_repo = Repo("/app")

    sha = local_repo.git.hash_object('data/000001-42.600.2.tif')

    print("sha for data/000001-42.600.2.tif (git hash-object data/000001-42.600.2.tif)", sha)


if __name__ == "__main__":
    # https://pygithub.readthedocs.io
    repo_token = os.environ["INPUT_REPO_TOKEN"]
    main(repo_token)
