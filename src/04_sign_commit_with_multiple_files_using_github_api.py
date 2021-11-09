import datetime
import os
import github

from pprint import pprint


# If you run this example using your personal token the commit is not going to be verified.
# It only works for commits made using a token generated for a bot/app like the one you have
# during the workflow job execution.
# The example workflow "example-04.yml" uses the GITHUB_TOKEN and auto-commits are verified.

def main(repo_token, branch):

    gh = github.Github(repo_token)

    repository = "josecelano/pygithub"

    remote_repo = gh.get_repo(repository)

    # Update files:
    #   data/example-04/latest_datetime_01.txt
    #   data/example-04/latest_datetime_02.txt
    # with the current date.

    file_to_update_01 = "data/example-04/latest_datetime_01.txt"
    file_to_update_02 = "data/example-04/latest_datetime_02.txt"

    now = datetime.datetime.now()

    file_to_update_01_content = str(now)
    file_to_update_02_content = str(now)

    blob1 = remote_repo.create_git_blob(file_to_update_01_content, "utf-8")
    element1 = github.InputGitTreeElement(
        path=file_to_update_01, mode='100644', type='blob', sha=blob1.sha)

    blob2 = remote_repo.create_git_blob(file_to_update_02_content, "utf-8")
    element2 = github.InputGitTreeElement(
        path=file_to_update_02, mode='100644', type='blob', sha=blob2.sha)

    commit_message = f'Example 04: update datetime to {now}'

    branch_sha = remote_repo.get_branch(branch).commit.sha

    print("Branch sha: ", branch_sha)

    base_tree = remote_repo.get_git_tree(sha=branch_sha)

    print("Base tree: ", base_tree)

    tree = remote_repo.create_git_tree([element1, element2], base_tree)

    print("Tree: ", tree)

    parent = remote_repo.get_git_commit(sha=branch_sha)

    print("Parent: ", parent)

    commit = remote_repo.create_git_commit(commit_message, tree, [parent])

    print("New commit: ", commit)

    branch_refs = remote_repo.get_git_ref(f'heads/{branch}')

    print("Banch refs: ", branch_refs)

    branch_refs.edit(sha=commit.sha)

    print("New branch ref: ", commit.sha)


if __name__ == "__main__":
    # https://pygithub.readthedocs.io
    repo_token = os.environ["INPUT_REPO_TOKEN"]
    branch = os.environ["INPUT_BRANCH"]
    main(repo_token, branch)
