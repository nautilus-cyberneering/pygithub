import datetime
import os
from pprint import pprint

from github import Github


# If you run this example using your personal token the commit is not going to be verified.
# It only works for commits made using a token generated for a bot/app like the one you have
# during the workflow job execution.
# The example workflow "example-01.yml" uses the GITHUB_TOKEN and auto-commits are verified.

def main(repo_token, branch):

    gh = Github(repo_token)

    repository = "josecelano/pygithub"

    remote_repo = gh.get_repo(repository)

    # Update file data/example-01/latest_datetime.txt with the current date.

    file_to_update = "data/example-01/latest_datetime.txt"

    # Get current file sha

    dir_content = remote_repo.get_contents("data/example-01", branch)

    remote_sha = None

    for file in dir_content:
        if (file.path == file_to_update):
            print("File: ", file.path, " sha:", file.sha)
            remote_sha = file.sha

    if remote_sha is None:
        raise ValueError(f'File not found {file_to_update}')

    # Update file

    now = datetime.datetime.now()
    print("Datetime:", now)

    commit_message = f'Example 01: update datetime to {now}'

    response = remote_repo.update_file(
        file_to_update, commit_message, str(now), remote_sha, branch)

    pprint(response)
    print("Commit sha: ", response['commit'].sha)


if __name__ == "__main__":
    # https://pygithub.readthedocs.io
    repo_token = os.environ["INPUT_REPO_TOKEN"]
    branch = "main"
    main(repo_token, branch)
