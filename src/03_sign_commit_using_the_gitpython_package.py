import os
import pprint
import random

import gnupg
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


def execute_console_command(command):
    print(f'Executing command: {command}')
    output = os.popen(command).read()
    print(output)


def print_git_config_option(option):
    command = f'git config --get {option}'
    print(f'Executing command: {command}')
    output = os.popen(command).read()
    print(output)


def commit_without_signning(temp_dir, repo):
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


def signed_commit(temp_dir, repo, gpg_private_key, passphrase):

    # Create file
    filename = "README_SIGNED.md"
    file_path = temp_dir + '/' + filename
    print(f'Creating file: {file_path}')
    open(file_path, 'w').close()

    # Add the new file to the index
    print(f'Adding file "{filename}" to the index')
    index = repo.index
    index.add([file_path])

    # Needed for commit with signature:
    # https://github.com/gitpython-developers/GitPython/issues/580#issuecomment-282474086
    index.write()

    # TODO: get from console, gnupg package or env var
    signingkey = '27304EDD6079B81C'
    keygrip = '449972AC9FF11BCABEED8A7AE834C4349CC4DBFF'
    subkey_keygrip = '97D36F5B8F5BECDA8A1923FC00D11C7C438584F9'
    fingerprint = '88966A5B8C01BD04F3DA440427304EDD6079B81C'
    hex_passphrase = passphrase.encode('utf-8').hex().upper()

    # git config --global user.name "A committer"
    repo.config_writer().set_value("user", "name", "A committer").release()
    # git config --global user.email "committer@example.com"
    repo.config_writer().set_value("user", "email", "committer@example.com").release()

    gpg = gnupg.GPG(gnupghome='/root/.gnupg', verbose=False, use_agent=True)

    # Import private key
    result = gpg.import_keys(gpg_private_key, passphrase=passphrase)
    # print(gpg_private_key, passphrase)
    pprint.pprint(result)

    # Print gpg keys using Python package
    keys = gpg.list_keys(True)
    # pprint.pprint(keys)

    # Preset passphrase using gpg-connect-agent:
    preset_passphrase_command = f'gpg-connect-agent \'PRESET_PASSPHRASE {keygrip} -1 {hex_passphrase}\' /bye'
    execute_console_command(preset_passphrase_command)

    repo.git.commit('-S', f'--gpg-sign={signingkey}', '-m', '"my signed commit"',
                    author='"A committer <committer@example.com>"')

    # Print commit info
    execute_console_command(f'cd {temp_dir} && git log --show-signature')


def main(gpg_private_key, passphrase):
    temp_dir = create_temp_dir()
    repo = git_init(temp_dir)

    print("COMMIT WITHOUT SIGNATURE")
    print("------------------------")
    commit_without_signning(temp_dir, repo)

    print("COMMIT WITH SIGNATURE")
    print("---------------------")
    signed_commit(temp_dir, repo, gpg_private_key, passphrase)


if __name__ == "__main__":
    # https://gitpython.readthedocs.io/

    # Get environment variables
    gpg_private_key = os.getenv('GPG_PRIVATE_KEY').replace(r'\n', '\n')
    passphrase = os.environ.get('PASSPHRASE')

    main(gpg_private_key, passphrase)
