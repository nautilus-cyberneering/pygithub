# How to create a single commit with multiple files using GitHub API

1. [Solution 01: Using GitHub REST API](#solution-01-using-gitHub-rest-api)
2. [Solution 02: Using GitHub GraphQL API](#solution-02-using-github-graphql-api)
3. [Links](#links)

## Solution 01: Using GitHub REST API

> Git was initially a toolkit for a version control system rather than a complete, user-friendly VCS. It has many subcommands that do low-level work, and they were designed to be chained together UNIX-style or called from scripts. These commands are generally called Git's "plumbing" commands, while the more user-friendly commands are called "porcelain".

From: [Git Book - 10.1 Git Internals - Plumbing and Porcelain](https://git-scm.com/book/en/v2/Git-Internals-Plumbing-and-Porcelain)

We recommend reading chapter 10 of the [Git book](https://git-scm.com/book/en/v2/Git-Internals-Plumbing-and-Porcelain).

"Git is a content-addressable filesystem". It has a key-value database. You can store different objects inside the database: `blobs`, `trees` and `commits`. Before jumping into the GitHub examples, we must understand the low-level Git commands because the GitHub API is only a wrapper for those low-level commands. There is no high-level command on the REST API similar to `git commit`. Instead of that, the REST API works like the low-level git commands.

> IMPORTANT: with the new [GrapQL GitHub API](https://github.blog/changelog/2021-09-13-a-simpler-api-for-authoring-commits), you can do something more similar to what you usually do at a higher level with the `git commit` command.

In order to understand the Python code, we will do the same using low-level git commands.

Let's start creating and initializing a new git repo:

```shell
mkdir example-04
cd example-04/
git init
```

The most basic git object is the `blob` object. The `blob` object contains the file contents. If you want to get the list of objects in your git database, you can execute this command:

```shell
find .git/objects -type f
```

At this point, it is still empty.

Since we want to add two new files, we need to create two `blob` objects with the content of the files. Both files only contain the current date and time.

```shell
echo '2021-11-19 00:18:44.628530' | git hash-object -w --stdin
```

The output for the command is the SHA-1 hash of the object:

```text
392aab2ab92b615a7bf51bfb59c1f00443bbefd6
```

And we create the `blob` object for the second file:

```shell
echo '2021-11-19 12:49:44.628530' | git hash-object -w --stdin
1b9b5bc6d931d46d2e765d7c46f266bb261161a0
```

The ' -w' option tells the command to write the object to the database.

If we list the objects again, we get the two new objects:

```shell
find .git/objects -type f
.git/objects/1b/9b5bc6d931d46d2e765d7c46f266bb261161a0
.git/objects/39/2aab2ab92b615a7bf51bfb59c1f00443bbefd6
```

We can get the file content (`blob`) from the database using the SHA-1 hash:

```shell
git cat-file -p 1b9b5bc6d931d46d2e765d7c46f266bb261161a0
2021-11-19 12:49:44.628530
```

We can now write the files getting the content from the Git database:

```shell
git cat-file -p 392aab2ab92b615a7bf51bfb59c1f00443bbefd6 > latest_datetime_01.txt
git cat-file -p 1b9b5bc6d931d46d2e765d7c46f266bb261161a0 > latest_datetime_02.txt
```

In the Python example, the line to create the `blob` object is this one:

```python
blob1 = remote_repo.create_git_blob(file_to_update_01_content, "utf-8")
```

We are using a [Python package](https://github.com/PyGithub/PyGithub) which is a wrapper for the GitHub REST API.

The only way to get the data is by using its SHA and we do not have the filename store anywhere yet. The way git stores the filename is by using another object in the database: the `tree`. The simplest `tree` object only contains a reference to one `blob` object. The `tree` is like a directory with the list of files where the contents of the files are the `blob` objects. We need to create a dir (`tree`) also for only one file because Git will add the file metadata there. The same object is used for one an multiple files. The `tree` can also contain another `tree`.

In order to create the `tree`, we need to take the state of the staging area. You first have to set up an index by staging some files with these commands:

```shell
git update-index --add --cacheinfo 100644 392aab2ab92b615a7bf51bfb59c1f00443bbefd6 latest_datetime_01.txt
git update-index --add --cacheinfo 100644 1b9b5bc6d931d46d2e765d7c46f266bb261161a0 latest_datetime_02.txt
```

If you run `git status` at this point, you will see something like:

```text
On branch main

No commits yet

Changes to be committed:
  (use "git rm --cached <file>..." to unstage)
	new file:   latest_datetime_01.txt
	new file:   latest_datetime_02.txt
```

Now we need to write the `tree` with:

```shell
git write-tree
cbd0df2b16d8398f43769d2adb29d43ad7f94e93
```

The output is the new object hash, which you can use to get the object content:

```shell
git cat-file -p cbd0df2b16d8398f43769d2adb29d43ad7f94e93
100644 blob 392aab2ab92b615a7bf51bfb59c1f00443bbefd6	latest_datetime_01.txt
100644 blob 1b9b5bc6d931d46d2e765d7c46f266bb261161a0	latest_datetime_02.txt
```

If you list all objects again, now you will see the new `tree` object:

```shell
find .git/objects -type f
.git/objects/cb/d0df2b16d8398f43769d2adb29d43ad7f94e93
.git/objects/1b/9b5bc6d931d46d2e765d7c46f266bb261161a0
.git/objects/39/2aab2ab92b615a7bf51bfb59c1f00443bbefd6
```

The corresponding Python code for this step is:

```python
element1 = github.InputGitTreeElement(
    path=file_to_update_01, mode='100644', type='blob', sha=blob1.sha)
```

We have the files with the right content but still need to create the `commit`. The `commit` object if the object where Git stores this information:

- Hash of the top-level tree for the snapshot of the project at that point.
- The parent `commit`. In this step-by-step explanation, we are using a new repository, but we are adding it in a branch containing other commits in the complete Python example.
- The author information.
- Blank line.
- Commit message.

We can create the `commit` with:

```shell
echo 'First commit' | git commit-tree cbd0df2b16d8398f43769d2adb29d43ad7f94e93
7d696c8c8d75c0d25aa470ac8015a886b6350994
```

The output is the hash of the commit object (you will get a different hash value because of different creation time and author data):

```shell
git cat-file -p 7d696c8c8d75c0d25aa470ac8015a886b6350994
tree cbd0df2b16d8398f43769d2adb29d43ad7f94e93
author Jose Celano <jose.celano@email.com> 1637329203 +0000
committer Jose Celano <jose.celano@email.com> 1637329203 +0000

First commit
```

And you can get the `commit` info using the hash:

```shell
find .git/objects -type f
.git/objects/39/2aab2ab92b615a7bf51bfb59c1f00443bbefd6 <- first blob object
.git/objects/1b/9b5bc6d931d46d2e765d7c46f266bb261161a0 <- second blob object
.git/objects/cb/d0df2b16d8398f43769d2adb29d43ad7f94e93 <- the tree
.git/objects/7d/696c8c8d75c0d25aa470ac8015a886b6350994 <- the commit


git log --stat 7d696c8c8d75c0d25aa470ac8015a886b6350994
commit 7d696c8c8d75c0d25aa470ac8015a886b6350994
Author: Jose Celano <josecelano@gmail.com>
Date:   Fri Nov 19 13:40:03 2021 +0000

    First commit

 latest_datetime_01.txt | 1 +
 latest_datetime_02.txt | 1 +
 2 files changed, 2 insertions(+)
```

The Python code is a little bit more complex because we need to get the parent commit:

```python
# Get parent info
branch_sha = remote_repo.get_branch(branch).commit.sha
parent = remote_repo.get_git_commit(sha=branch_sha)
# Create the tree with he two files. Every file is another tree.
base_tree = remote_repo.get_git_tree(sha=branch_sha)
tree = remote_repo.create_git_tree([element1, element2], base_tree)
# Create the commit
commit = remote_repo.create_git_commit(commit_message, tree, [parent])
```

We have done so far only: `git add -A && git commit -m "First commit"`. We need to update the reference for our current `main` branch.

Git uses references as an alias for commits. A reference is a file that contains the hash of the commit. Since this is our first `commit` in the repo we do not have yet a reference to the HEAD of the branch.


```shell
find .git/refs
.git/refs
.git/refs/tags
.git/refs/heads

ls -al .git/refs/heads
total 8
drwxrwxr-x 2 josecelano josecelano 4096 nov 19 12:39 .
drwxrwxr-x 4 josecelano josecelano 4096 nov 19 12:39 ..
```

We need to create it manually. If we want to update our `main` branch with the new commit we can use the command `git update-ref refs/heads/main 7d696c8c8d75c0d25aa470ac8015a886b6350994`. That command will create the file `.git/refs/heads/main` containing your commit hash.

```shell
git update-ref refs/heads/main 7d696c8c8d75c0d25aa470ac8015a886b6350994

cat .git/refs/heads/main
7d696c8c8d75c0d25aa470ac8015a886b6350994

git log
commit 7d696c8c8d75c0d25aa470ac8015a886b6350994 (HEAD -> main)
Author: Jose Celano <josecelano@gmail.com>
Date:   Fri Nov 19 13:40:03 2021 +0000

    First commit
```

In Python, we do that with these two lines:

```python
# Get the reference for the rbach we are workign on
branch_refs = remote_repo.get_git_ref(f'heads/{branch}')
# Update the reference to the new commit
branch_refs.edit(sha=commit.sha)
```

You can read and execute the complete example [here](../src/04_sign_commit_with_multiple_files_using_github_api.py).

The example creates a single commit that modifies the content of two files:

```text
latest_datetime_01.txt
latest_datetime_02.txt
```

The simplified version of the example:

```python
import datetime
import os
import github

def main(repo_token, branch):

    gh = github.Github(repo_token)

    repository = "josecelano/pygithub"

    remote_repo = gh.get_repo(repository)

    file_to_update_01 = "latest_datetime_01.txt"
    file_to_update_02 = "latest_datetime_02.txt"

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

    base_tree = remote_repo.get_git_tree(sha=branch_sha)

    tree = remote_repo.create_git_tree([element1, element2], base_tree)

    parent = remote_repo.get_git_commit(sha=branch_sha)

    commit = remote_repo.create_git_commit(commit_message, tree, [parent])

    branch_refs = remote_repo.get_git_ref(f'heads/{branch}')

    branch_refs.edit(sha=commit.sha)

if __name__ == "__main__":
    repo_token = os.environ["INPUT_REPO_TOKEN"]
    branch = os.environ["INPUT_BRANCH"]
    main(repo_token, branch)
```

## Solution 02: Using GitHub GraphQL API

TODO

GraphQL API reference: <https://docs.github.com/en/graphql/reference/mutations#createcommitonbranch>

## Links

Committing multiple files to GitHub using REST API:

- [Stephan Hoyer - Javascript example - Committing multiple files to GitHub over API](https://gist.github.com/StephanHoyer/91d8175507fcae8fb31a)
- [Stackoverflow - Edit multiple files in single commit with GitHub API](https://stackoverflow.com/questions/61583403/edit-multiple-files-in-single-commit-with-github-api)
- [Paul Kinlan - Creating a Commit With Multiple Files to GitHub With JS on the Web](https://dzone.com/articles/creating-a-commit-with-multiple-files-to-github-wi)
- [Stackoverflow - How to create a commit and push into repo with GitHub API v3?](https://stackoverflow.com/questions/11801983/how-to-create-a-commit-and-push-into-repo-with-github-api-v3/14672793)

Committing multiple files to GitHub using GraphQL API:

- [The GitHub Blog - A simpler API for authoring commits](https://github.blog/changelog/2021-09-13-a-simpler-api-for-authoring-commits/)

Python and GraphQL:

- [GraphQL in Python Made Easy](https://github.com/graphql-python)

Python packages for GitHub API:

- [Python GitHub REST API](https://pypi.org/project/PyGithub)
- [Python GitHub GraphQL API](https://pypi.org/project/gql)

GitHub documentation:

- [GraphQL API - createCommitOnBranch](https://docs.github.com/en/graphql/reference/mutations#createcommitonbranch)

Others:

- [Steve Martinelli - Comparing GitHub’s REST and GraphQL APIs](https://www.stevemar.net/github-graphql-vs-rest/)
- [Git Internals](https://git-scm.com/book/en/v2/Git-Internals-Plumbing-and-Porcelain)
