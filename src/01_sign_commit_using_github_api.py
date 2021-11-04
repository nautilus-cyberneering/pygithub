import datetime
import os
from pprint import pprint

from github import Github


# If you run this example using your personal token the commit is not going to be verified.
# It only works for commits made using a token generated for a bot/app like the one you have
# during the workflow job execution.
# The sample workflow "sample-01.yml" uses the GITHUB_TOKEN and auto-commits are verified.

def main(repo_token):

    gh = Github(repo_token)

    repository = "josecelano/pygithub"

    remote_repo = gh.get_repo(repository)

    # Update file data/latest_datetime.txt with the current date.

    file_to_update = "data/latest_datetime.txt"

    # Get current file sha

    dir_content = remote_repo.get_contents("data", "main")

    for file in dir_content:
        if (file.path == file_to_update):
            print("File: ", file.path, " sha:", file.sha)
            remote_sha = file.sha

    # Update file

    now = datetime.datetime.now()
    print("Datetime:", now)

    commit_message = f'update datetime to {now}'
    branch = "main"

    response = remote_repo.update_file(
        file_to_update, commit_message, str(now), remote_sha, branch)

    pprint(response)
    print("Commit sha: ", response['commit'].sha)


if __name__ == "__main__":
    # https://pygithub.readthedocs.io
    repo_token = os.environ["INPUT_REPO_TOKEN"]
    main(repo_token)
