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


def main(gpg_private_key, passphrase):
    temp_dir = create_temp_dir()
    repo = git_init(temp_dir)

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
    # Of master key 88966A5B8C01BD04F3DA440427304EDD6079B81C
    keygrip = '449972AC9FF11BCABEED8A7AE834C4349CC4DBFF'
    hex_passphrase = passphrase.encode('utf-8').hex().upper()

    # Set global Git user
    repo.config_writer().set_value("user", "name", "A committer").release()
    repo.config_writer().set_value("user", "email", "committer@example.com").release()

    # Import private key
    gpg = gnupg.GPG(gnupghome='/root/.gnupg', verbose=False, use_agent=True)
    gpg.import_keys(gpg_private_key, passphrase=passphrase)

    # Preset passphrase using gpg-connect-agent:
    preset_passphrase_command = f'gpg-connect-agent \'PRESET_PASSPHRASE {keygrip} -1 {hex_passphrase}\' /bye'
    execute_console_command(preset_passphrase_command)

    repo.git.commit('-S', f'--gpg-sign={signingkey}', '-m', '"my signed commit"',
                    author='"A committer <committer@example.com>"')

    # Print commit info
    execute_console_command(f'cd {temp_dir} && git log --show-signature')


if __name__ == "__main__":
    # https://gitpython.readthedocs.io/

    # Get environment variables
    gpg_private_key = os.getenv('GPG_PRIVATE_KEY').replace(r'\n', '\n')
    passphrase = os.environ.get('PASSPHRASE')

    main(gpg_private_key, passphrase)
