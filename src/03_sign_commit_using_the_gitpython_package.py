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

    # gpg commands:
    # List keys:          gpg --list-secret-keys --keyid-format=long
    # Show public key:    gpg --armor --export 27304EDD6079B81C
    # Export private key: gpg --output private_key.pgp --armor --export-secret-key 27304EDD6079B81C
    # Export private key:
    # (for env var)       gpg -a --export-secret-keys 88966A5B8C01BD04F3DA440427304EDD6079B81C | cat -e | sed 's/\$/\\n/g'
    # Import pgp key:     echo -e $GPG_PRIVATE_KEY | gpg --import
    # Get keygrips:       gpg --batch --with-colons --with-keygrip --list-secret-keys
    #                     gpg --with-keygrip --list-secret-keys

    # Needed for commit with signature:
    # https://github.com/gitpython-developers/GitPython/issues/580#issuecomment-282474086
    index.write()

    # TODO: get from console, gnupg package or env var
    signingkey = '27304EDD6079B81C'
    keygrip = '97D36F5B8F5BECDA8A1923FC00D11C7C438584F9'
    fingerprint = '88966A5B8C01BD04F3DA440427304EDD6079B81C'
    hex_passphrase = passphrase.encode('utf-8').hex().upper()

    # git config --global user.name "A committer"
    repo.config_writer().set_value("user", "name", "A committer").release()
    # git config --global user.email "committer@example.com"
    repo.config_writer().set_value("user", "email", "committer@example.com").release()
    repo.config_writer().set_value("user", "signingkey", signingkey).release()
    repo.config_writer().set_value("commit", "gpgsign", "true").release()

    # Debug: git Python package does not write global options on the root git config file
    # print_git_config_option('user.name')
    # print_git_config_option('user.email')
    # print_git_config_option('user.signingkey')
    # print_git_config_option('commit.gpgsign')

    gpg = gnupg.GPG(gnupghome='/root/.gnupg', verbose=True, use_agent=True)

    # Import private key
    result = gpg.import_keys(gpg_private_key, passphrase=passphrase)
    # print(gpg_private_key, passphrase)
    pprint.pprint(result)

    # Print gpg keys using Python package
    # keys = gpg.list_keys()
    # pprint.pprint(keys)
    keys = gpg.list_keys(True)
    # pprint.pprint(keys)

    # Print gpg keys using console command
    execute_console_command('gpg --list-secret-keys --keyid-format=long')
    # Print GPG agent conf
    execute_console_command('cat /root/.gnupg/gpg-agent.conf')
    # Print global git config. With docker we use root user and it does not have a .gitconfig file
    execute_console_command('cat ~/.gitconfig')

    # Reload PGP agent
    # reload_pgp_agent_command = 'gpg-connect-agent reloadagent /bye'
    # execute_console_command(reload_pgp_agent_command)
    #execute_console_command('gpg-agent --daemon --allow-preset-passphrase')

    #reload_agent_command = f'gpg-connect-agent \'RELOADAGENT\' /bye'
    # execute_console_command(reload_agent_command)

    gpg_agente_config = 'gpg-agent --gpgconf-list'
    execute_console_command(gpg_agente_config)

    # Preset passphrase using gpg-preset-passphrase:
    # https://www.gnupg.org/documentation/manuals/gnupg/Invoking-gpg_002dpreset_002dpassphrase.html#Invoking-gpg_002dpreset_002dpassphrase
    # This command makes git not prompt for passphrase for GPG key. We preset the PGP agent with the passphrase
    # preset_passphrase_command = f'echo \'{passphrase}\' | /usr/lib/gnupg2/gpg-preset-passphrase -v --preset {keygrip}'
    # execute_console_command(preset_passphrase_command)

    # Preset passphrase using gpg-connect-agent:
    # https://www.gnupg.org/documentation/manuals/gnupg/Agent-PRESET_005fPASSPHRASE.html#Agent-PRESET_005fPASSPHRASE
    # https://github.com/crazy-max/ghaction-import-gpg/blob/60f6f3e9a98263cc2c51ebe1f9babe82ded3f0ba/src/gpg.ts#L170-L174
    preset_passphrase_command = f'gpg-connect-agent \'PRESET_PASSPHRASE {keygrip} -1 {hex_passphrase}\' /bye'
    execute_console_command(preset_passphrase_command)

    # If we want ot ask the user for the passphrase (popup)
    # https://www.gnupg.org/documentation/manuals/gnupg/Agent-GET_005fPASSPHRASE.html#Agent-GET_005fPASSPHRASE
    # error = 'error'
    # prompt = 'prompt'
    # desc = 'desc'
    # get_passphrase_command = f'gpg-connect-agent \'GET_PASSPHRASE {keygrip} error prompt desc\' /bye'
    # execute_console_command(get_passphrase_command)

    show_key_info_command = f"gpg-connect-agent 'KEYINFO {keygrip}' /bye"
    execute_console_command(show_key_info_command)

    repo.git.commit('-S', f'--gpg-sign={signingkey}', '-m', '"my commit message 2"',
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
