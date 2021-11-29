import os
import pprint
import random

from git import Actor, Repo


def create_temp_dir():
    # Create temp dir
    dir_name = random.getrandbits(128)
    temp_dir = f'/tmp/{dir_name}'
    print(f'Creating temp dir: {temp_dir}')
    os.mkdir(temp_dir)
    return temp_dir


def git_init(temp_dir):
    print('Initializing repo ...')
    repo = Repo.init(temp_dir)
    return repo


def main():
    temp_dir = create_temp_dir()
    repo = git_init(temp_dir)

    # Create file
    filename = "README.md"
    file_path = temp_dir + '/' + filename
    print(f'Creating file: {file_path}')
    open(file_path, 'w').close()

    # Add the new file to the index (staging area)
    print(f'Adding file "{filename}" to the index')
    index = repo.index
    index.add([file_path])

    # Commit without signature
    author = Actor("An author", "author@example.com")
    index.commit("my commit message", author=author)

    # Print commit info
    command = f'cd {temp_dir} && git log'
    print(f'Executing command: {command}')
    output = os.popen(command).read()
    print(output)


if __name__ == "__main__":
    # https://gitpython.readthedocs.io/
    main()
