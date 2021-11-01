import base64
import hashlib
import os
from pprint import pprint

from git import Repo
from github import Github


def main(repo_token):
    gh = Github(repo_token)

    repository = "josecelano/pygithub"

    remote_repo = gh.get_repo(repository)

    # Get commit

    commit = remote_repo.get_commit("03aaa45f46b313ed6079cd2e8788173bd0a3af52")

    pprint(commit)

    # Get issue

    issue = remote_repo.get_issue(number=1)

    pprint(issue)

    # Get file content

    # 1 MB limit
    file_content = remote_repo.get_contents("data/.gitkeep", "main")

    pprint(file_content)

    # Get dir info

    # 1 MB limit
    dir_content = remote_repo.get_contents("data", "main")

    for file in dir_content:
        print("File: ", file.path, " sha:", file.sha)

    pprint(dir_content)    

    # Calculate file hash

    local_repo = Repo("/app")

    sha = local_repo.git.hash_object('data/000001-42.600.2.tif')

    print("sha for data/000001-42.600.2.tif (git hash-object data/000001-42.600.2.tif)", sha)

    # Update binary file. Update data/000002-42.600.2.tif with the same content

    # branch = "main"
    # commit_message = f'Update file data/000001-42.600.2.tif'
    # content = open("data/000001-42.600.2.tif", "rb").read()
    # content_base64 = base64.encodebytes(content)
    # response = remote_repo.update_file(
    #     "000002-42.600.2.tif", commit_message, content, sha, branch)


if __name__ == "__main__":
    # https://pygithub.readthedocs.io
    repo_token = os.environ["INPUT_REPO_TOKEN"]
    main(repo_token)
