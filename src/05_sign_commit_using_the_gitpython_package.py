import os
import random

from git import Actor, Repo


def main():

    # Create temp dir
    dir_name = random.getrandbits(128)
    temp_dir = f'/tmp/{dir_name}'
    print(f'Creating temp dir: {temp_dir}')
    os.mkdir(temp_dir)

    print('Initializing repo ...')
    repo = Repo.init(temp_dir)

    #
    #  Commit without signature
    #

    # Create file
    filename = "README.md"
    file_path = temp_dir + '/' + filename
    print(f'Creating file: {file_path}')
    open(file_path, 'w').close()

    # Add the new file to the index
    print(f'Adding file "{filename}" to the index')
    index = repo.index
    index.add([file_path])

    # Commit without signature
    author = Actor("An author", "author@example.com")
    committer = Actor("A committer", "committer@example.com")
    index.commit("my commit message", author=author, committer=committer)

    # Print commit info
    command = f'cd {temp_dir} && git log'
    print(f'Executing command: {command}')
    output = os.popen(command).read()
    print(output)

    #
    #  Commit with signature
    #

    # The GPG key:
    # sec   rsa4096/27304EDD6079B81C 2021-11-19 [SC]
    #       88966A5B8C01BD04F3DA440427304EDD6079B81C
    # uid                 [ultimate] A committer <committer@example.com>
    # ssb   rsa4096/5B6BDD35BEDFBF6F 2021-11-19 [E]

    # Create file
    filename = "README_SIGNED.md"
    file_path = temp_dir + '/' + filename
    print(f'Creating file: {file_path}')
    open(file_path, 'w').close()

    # Add the new file to the index
    print(f'Adding file "{filename}" to the index')
    index = repo.index
    index.add([file_path])

    # List keys: gpg --list-secret-keys --keyid-format=long
    # Show public key: gpg --armor --export 5B6BDD35BEDFBF6F

    # Commit with signature
    index.write()

    signingkey = '5B6BDD35BEDFBF6F'
    repo.config_writer().set_value("user", "name", "A committer").release()
    repo.config_writer().set_value("user", "email", "committer@example.com").release()
    repo.config_writer().set_value("user", "signingkey", signingkey).release()
    repo.config_writer().set_value("commit", "gpgsign", "true").release()

    # TODO: set up private key from env varaible like "crazy-max/ghaction-import-gpg" action

    repo.git.commit('-S', f'--gpg-sign={signingkey}', '-m', 'my commit message 2',
                    author='A committer <committer@example.com>')

    # Print commit info
    command = f'cd {temp_dir} && git log'
    print(f'Executing command: {command}')
    output = os.popen(command).read()
    print(output)


if __name__ == "__main__":
    # https://gitpython.readthedocs.io/
    main()
