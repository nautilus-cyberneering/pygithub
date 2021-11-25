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


def execute_console_command(command, show_ouput=False):
    output = os.popen(command).read()
    if (show_ouput):
        print(output)
    return output


def get_keygrip_by(fingerprint):
    """
    This function parses the keygrip of a given GPG kye using the gpg console command and parsing the output.

    Sample output for the command:
    sec:-:4096:1:27304EDD6079B81C:1637342753:::-:::scESC:::+:::23::0:
    fpr:::::::::88966A5B8C01BD04F3DA440427304EDD6079B81C:
    grp:::::::::449972AC9FF11BCABEED8A7AE834C4349CC4DBFF:
    uid:-::::1637342753::B3B0B2247600E80BAB9D4802D5CF0AFC477DE016::A committer <committer@example.com>::::::::::0:
    ssb:-:4096:1:5B6BDD35BEDFBF6F:1637342753::::::e:::+:::23:
    fpr:::::::::B1D4A2483D1D2A02416BE0775B6BDD35BEDFBF6F:
    grp:::::::::97D36F5B8F5BECDA8A1923FC00D11C7C438584F9:

    In that example the keygrip (grp) of the key 88966A5B8C01BD04F3DA440427304EDD6079B81C is 449972AC9FF11BCABEED8A7AE834C4349CC4DBFF

    Specification for the format: https://github.com/CSNW/gnupg/blob/master/doc/DETAILS
    """

    output = execute_console_command(
        f'gpg --batch --with-colons --with-keygrip --list-secret-keys {fingerprint}', False)

    records = output.split("\n")

    current_fingerprint = ''

    for record in records:
        if record.startswith('fpr'):
            fields = record.split(':')
            current_fingerprint = fields[9]
        if record.startswith('grp'):
            fields = record.split(':')
            keygrip = fields[9]
            if (current_fingerprint == fingerprint):
                return keygrip

    return None


def get_short_key_id_from_fingerprint(fingerprint):
    """
    fingerprint = 88966A5B8C01BD04F3DA440427304EDD6079B81C

    Fingerprint: 8896 6A5B 8C01 BD04  F3DA 4404 2730 4EDD 6079 B81C
    Long key ID:                                2730 4EDD 6079 B81C
    Short key ID:                                         6079 B81C

    Returns: 6079B81C
    """
    return fingerprint[24:]


def import_gpg_private_key(gpg_private_key, passphrase):
    """
    Import PGP key into the the local keyring
    """
    gpg = gnupg.GPG(gnupghome='/root/.gnupg', verbose=False, use_agent=True)

    import_result = gpg.import_keys(gpg_private_key, passphrase=passphrase)
    fingerprint = import_result.fingerprints[0]

    keygrip = get_keygrip_by(fingerprint)

    short_key_id = get_short_key_id_from_fingerprint(fingerprint)

    # print(f'Fingerprint: {fingerprint}')
    # print(f'Short key ID: {short_key_id}')
    # print(f'Keygrip: {keygrip}')

    return keygrip, short_key_id


def preset_passphrase(keygrip, passphrase):
    """
    Preset passphrase using gpg-connect-agent in order to avoid prompting the user for it.
    """
    hex_passphrase = passphrase.encode('utf-8').hex().upper()
    preset_passphrase_command = f'gpg-connect-agent \'PRESET_PASSPHRASE {keygrip} -1 {hex_passphrase}\' /bye'
    execute_console_command(preset_passphrase_command)


def set_git_glogal_user_config(repo):
    """
    This configuration prevents from having this git error:

    stderr: 'Committer identity unknown

    *** Please tell me who you are.

    Run

    git config --global user.email "you@example.com"
    git config --global user.name "Your Name"

    to set your account's default identity.
    Omit --global to set the identity only in this repository.

    fatal: unable to auto-detect email address (got 'root@b37fb619ac5a.(none)')'
    """
    repo.config_writer().set_value("user", "name", "A committer").release()
    repo.config_writer().set_value("user", "email", "committer@example.com").release()


def create_signed_commit(temp_dir, signingkey):
    # Initialize the Git repo
    repo = git_init(temp_dir)

    # Git config
    set_git_glogal_user_config(repo)

    # Create new file to commit
    filename = "README_SIGNED.md"
    file_path = temp_dir + '/' + filename
    print(f'Creating file: {file_path}')
    open(file_path, 'w').close()

    # Add the new file to the index
    print(f'Adding file "{filename}" to the index')
    index = repo.index
    index.add([file_path])

    # Write index. Needed for commit with signature:
    # https://github.com/gitpython-developers/GitPython/issues/580#issuecomment-282474086
    index.write()

    # Signed commit
    repo.git.commit(
        '-S', f'--gpg-sign={signingkey}', '-m', '"my signed commit"')


def print_commit_info(temp_dir):
    execute_console_command(f'cd {temp_dir} && git log --show-signature', True)


def main(temp_dir, gpg_private_key, passphrase):

    keygrip, signingkey = import_gpg_private_key(gpg_private_key, passphrase)

    preset_passphrase(keygrip, passphrase)

    create_signed_commit(temp_dir, signingkey)

    print_commit_info(temp_dir)


if __name__ == "__main__":
    # https://gitpython.readthedocs.io/

    # Get environment variables
    gpg_private_key = os.getenv('GPG_PRIVATE_KEY').replace(r'\n', '\n')
    passphrase = os.environ.get('PASSPHRASE')

    # Create temp dir for the example
    temp_dir = create_temp_dir()

    main(temp_dir, gpg_private_key, passphrase)
