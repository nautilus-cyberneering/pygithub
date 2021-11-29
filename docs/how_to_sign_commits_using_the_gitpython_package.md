# How to sign commits using the GitPython package

> [GitPython](https://github.com/gitpython-developers/GitPython) is a python library used to interact with git repositories, high-level like git-porcelain, or low-level like git-plumbing.

GitPython does not allow you to sign commits with its `git-porcelain` method. The way you can commit with GitPython is:

```python
repo = Repo(repo_dir)
index = repo.index
index.add([file_to_commit_path])
author = Actor("An author", "author@example.com")

index.commit("my commit message", author=author)
```

`index.commit` method does not provide any argument to sign commits. If you want to sign commits you have to use the the `git-plumbing` method `git.commit(...)`:

```python
repo = Repo(repo_dir)
index = repo.index
index.add([file_to_commit_path])
author = Actor("An author", "author@example.com")

index.write()
repo.git.commit('-S', f'--gpg-sign={signingkey}', '-m', "my commit message")
```

The `repo.git.commit` method is basically a wrapper for the git commit command. All the arguments you pass to it will be passed to the git commit command. Notice you have to call two methods:

```python
index.write()
repo.git.commit(arg, ...)
```

I do not know exactly why you need to `write` your changes but it is something the git commit wrapper does:

<https://github.com/gitpython-developers/GitPython/blob/88732b694068704cb151e0c4256a8e8d1adaff38/git/index/base.py#L938-L957>

And it's something [Sebastian Thiel](https://github.com/gitpython-developers/GitPython/issues/580#issuecomment-282474086) said it is needed.

So if you want to sign the commit, you only have to specify the signing key. The GitPython package relies on Git configuration, and Git relies on GPG configuration. What is happening under the hood is:

1. GitPython is going to call the git commit command using a [git binary wrapper](https://github.com/gitpython-developers/GitPython/blob/254305c935893d7578b112acfa814a07d398ae28/git/cmd.py#L171).
2. Git is going to call GPG command to sign the commit.
3. GPG is going to prompt you with the passphrase of the key.

As long as the GPG and Git configuration are OK, GitPython will sign the commit correctly. The [example 03](../03_sign_commit_using_the_gitpython_package) in this repo creates a newly signed commit, but before signing, it also sets up the GPG and Git configuration needed. In case you want to know how you can sign commits manually, you can follow other tutorials like:

- [Git Documentation - Git Tools - Signing Your Work](https://git-scm.com/book/en/v2/Git-Tools-Signing-Your-Work)
- [GitHub Documentation - Signing commits](https://docs.github.com/en/authentication/managing-commit-signature-verification/signing-commits)

I'm going to explain only how to do it automatically using Python. There are some steps you have to implement:

1. Import the GPG key
2. Preset the passphrase
3. Set Git global user

After those steps, you can call the GitPython commit method with the signing key ID you want to use.

## Import a GPG key using Python

When you create a new GPG key you can get the key info with the gpg command:

```shell
(base) josecelano@josecelano:~/Documents/github/josecelano/pygithub$ gpg -k -with-keygrip
/home/josecelano/.gnupg/pubring.kbx
-----------------------------------
pub   rsa4096 2021-11-19 [SC]
      88966A5B8C01BD04F3DA440427304EDD6079B81C
      Keygrip = 449972AC9FF11BCABEED8A7AE834C4349CC4DBFF
uid           [ultimate] A committer <committer@example.com>
sub   rsa4096 2021-11-19 [E]
      Keygrip = 97D36F5B8F5BECDA8A1923FC00D11C7C438584F9
```

For this example I've created the key `88966A5B8C01BD04F3DA440427304EDD6079B81C`. What I want to do is to export that key and import it later on the environment where I'm running the Python script.

You can export your GPG private key with:

```shell
gpg -a --export-secret-keys 6079B81C
```

and that will give you something like this:

```text
-----BEGIN PGP PRIVATE KEY BLOCK-----

lQdGBGGX3iEBEACqKHI35iK8y5lODg00/Uck4PDxxACldsT6OR01dmrDV2U0JYXw
...
I9wQBRMH4YdgH8UPp7FcEnPTvtQI+bVXUQm3N4YiOV+k
=JKJh
-----END PGP PRIVATE KEY BLOCK-----
```

To import the key using Python I'm using a Python package which is a [gpg wrapper](https://pypi.org/project/python-gnupg/).

```python
gpg = gnupg.GPG(gnupghome='/root/.gnupg', verbose=False, use_agent=True)
import_result = gpg.import_keys(gpg_private_key, passphrase=passphrase)
fingerprint = import_result.fingerprints[0]
```

The code is very simple. For this example, I'm passing both the private key and passphrase as environment variables. I'm using docker for the example and docker `.env` file for passing env vars. But since docker does not allow to use multi-line string values for variables, I had to store the private key as a one-line string and then convert it back to the standard multi-line version. That means the `gpg_private_key` variable contains something like:

```text
GPG_PRIVATE_KEY=-----BEGIN PGP PRIVATE KEY BLOCK-----\n\nl****************************\n-----END PGP PRIVATE KEY BLOCK-----\n
```

If you run the example using docker.

You also have to provide the `passphrase` which will be used to encrypt the private key. The method returns the fingerprint of the imported keys and the number of keys imported. The variable `import_result.fingerprints` contains this array:

```text
['88966A5B8C01BD04F3DA440427304EDD6079B81C', '88966A5B8C01BD04F3DA440427304EDD6079B81C']
```

I do not know why the primary key ID is duplicated. Maybe it's a bug, and it should return the fingerprint of the subkey (`97D36F5B8F5BECDA8A1923FC00D11C7C438584F9`). Anyway, for this example, I'm going to use the primary key, which is not a good practice, although Git and GitHub tutorials also use it. Please read the links below to know why it is not considered a good practice.

At this point, we have the key imported in our keyring but GPG it's going to ask us for the passphrase every time we sign something. The next section explains why you can avoid that.

## How to preset the GPG key passphrase

If you comment the code of the example to preset the passphrase you will get a popup like this:

![GPG prompt for passphrase](images/gpg-sign-prompt-for-passphrase.png)

any time you want to sign a commit. And we want to sign automatically. GPG has a way to avoid it even if you are doing it manually. You can use the `gpg-agent` which is a program that remembers your passphrase in order to avoid to type it again and again. You need to start the program and then tell it to store a new passprahse in advance. That way It won't ask you for the passphrase even the first time you need it.

There is a way to do it manually by using the [gpg-connect-agent](https://www.gnupg.org/documentation/manuals/gnupg/gpg_002dconnect_002dagent.html#:~:text=The%20gpg%2Dconnect%2Dagent%20is,output%20gets%20printed%20to%20stdout.) program. All you need to do is to connect to the agent and use the [`PRESET_PASSPHRASE`](https://www.gnupg.org/documentation/manuals/gnupg/Agent-PRESET_005fPASSPHRASE.html) command:

```shell
gpg-connect-agent "PRESET_PASSPHRASE $KEYGRIP -1 $HEX_PASSPHRASE" /bye
```

The Python code is very simple once you have the keygrip of the key you want to use to sign. We obtain the keygrip running another gpg command which gives you a formatted representation of the gpg key:

```text
sec:-:4096:1:27304EDD6079B81C:1637342753:::-:::scESC:::+:::23::0:
fpr:::::::::88966A5B8C01BD04F3DA440427304EDD6079B81C:
grp:::::::::449972AC9FF11BCABEED8A7AE834C4349CC4DBFF:
uid:-::::1637342753::B3B0B2247600E80BAB9D4802D5CF0AFC477DE016::A committer <committer@example.com>::::::::::0:
ssb:-:4096:1:5B6BDD35BEDFBF6F:1637342753::::::e:::+:::23:
fpr:::::::::B1D4A2483D1D2A02416BE0775B6BDD35BEDFBF6F:
grp:::::::::97D36F5B8F5BECDA8A1923FC00D11C7C438584F9:
```

Keygrips are stored on `grp:` records in a fixed field position.

Finally, the GPG configuration is completed. We only need to tell Git who is the user committing.

## How to config Git's global user

If we do not set the git user's configuration we get an error like this:

```text
stderr: 'Committer identity unknown

*** Please tell me who you are.

Run

git config --global user.email "you@example.com"
git config --global user.name "Your Name"

to set your account's default identity.
Omit --global to set the identity only in this repository.

fatal: unable to auto-detect email address (got 'root@b37fb619ac5a.(none)')'
```

The way we can run those git commands with Python is with:

```python
repo.config_writer().set_value("user", "name", "A committer").release()
repo.config_writer().set_value("user", "email", "committer@example.com").release()
```

We need to use the same author name and email that we have on the GPG key. Although the `gnupg` has some methods to get that information, I did it by parsing the output of the same gpg command again.

## Future improvements

The action shows some warnings:

```text
gpg: WARNING: unsafe permissions on homedir '/root/.gnupg'
gpg: WARNING: unsafe permissions on homedir '/root/.gnupg'
Creating file: /app/data/example-03/latest_datetime.txt
Adding file "data/example-03/latest_datetime.txt" to the index
commit 5d839b50415793b7ad1a858b692cfcd55ffa8ffd
gpg: WARNING: unsafe permissions on homedir '/root/.gnupg'
gpg: Signature made Thu Nov 25 17:54:58 2021 UTC
gpg:                using RSA key D7140A14E39CD9057C044047A3803B76B47860E0
gpg: Good signature from "Jose Celano (bot email, online key) <bot@josecelano.com>" [unknown]
gpg: WARNING: This key is not certified with a trusted signature!
gpg:          There is no indication that the signature belongs to the owner.
```

By the way, the GitHub Action I'm using in the workflows to import GPG keys also has the same warnings: <https://github.com/crazy-max/ghaction-import-gpg/issues/118>

## Acknowledges

Thanks to all the contributors of the [Import GPG GitHub Action](https://github.com/marketplace/actions/import-gpg). It would have taken me much more time to find the solution whithout following their Typescript solution.

And also to [Sebastian Thiel](https://github.com/Byron) who is one of the maintainers of the [GitPython](https://github.com/gitpython-developers/GitPython) package and who [pointed me and others to the right solution](https://github.com/gitpython-developers/GitPython/issues/580#issuecomment-282473867).

## Other mini Python examples

Set git congif option:

```python
# git config --global user.name "A committer"
repo.config_writer().set_value("user", "name", "A committer").release()
# git config --global user.email "committer@example.com"
repo.config_writer().set_value("user", "email", "committer@example.com").release()
repo.config_writer().set_value("user", "signingkey", signingkey).release()
repo.config_writer().set_value("commit", "gpgsign", "true").release()
```

Print gpg keys using `gnupg` Python package:

```python
import pprint
import gnupg

gpg = gnupg.GPG(gnupghome='/root/.gnupg', verbose=True, use_agent=True)
keys = gpg.list_keys(True)
pprint.pprint(keys)
```

## The GPG Key I'm using for the examples

```text
pub   rsa4096 2021-11-19 [SC]
      88966A5B8C01BD04F3DA440427304EDD6079B81C
      Keygrip = 449972AC9FF11BCABEED8A7AE834C4349CC4DBFF
uid           [ultimate] A committer <committer@example.com>
sub   rsa4096 2021-11-19 [E]
      Keygrip = 97D36F5B8F5BECDA8A1923FC00D11C7C438584F9
```

## Sample GPG commands

List your secret keys:

```shell
gpg --list-secret-keys --keyid-format=long
/home/josecelano/.gnupg/pubring.kbx
-----------------------------------
sec   rsa4096/27304EDD6079B81C 2021-11-19 [SC]
      88966A5B8C01BD04F3DA440427304EDD6079B81C
uid                 [ultimate] A committer <committer@example.com>
ssb   rsa4096/5B6BDD35BEDFBF6F 2021-11-19 [E]
```

Show public key:

```shell
gpg --armor --export 27304EDD6079B81C
-----BEGIN PGP PUBLIC KEY BLOCK-----

mQINBGGX3iEBEACqKHI35iK8y5lODg00/Uck4PDxxACldsT6OR01dmrDV2U0JYXw
...
```

Export private key:

```shell
gpg --output private_key.pgp --armor --export-secret-key 27304EDD6079B81C
-----BEGIN PGP PRIVATE KEY BLOCK-----
...
-----END PGP PRIVATE KEY BLOCK-----
```

Export private key in a single line (for `.env` file):

```shell
gpg -a --export-secret-keys 88966A5B8C01BD04F3DA440427304EDD6079B81C | cat -e | sed 's/\$/\\n/g'
```

Then you have to remove the real line breaks character. The final line in the docker `.env` file will look like this:

```text
GPG_PRIVATE_KEY=-----BEGIN PGP PRIVATE KEY BLOCK-----\n\nlXX\n-----END PGP PRIVATE KEY BLOCK-----\n
```

Import GPG key from env var:

```shell
echo -e $GPG_PRIVATE_KEY | gpg --import
```

Show keys using keygrip format:

```shell
gpg --batch --with-colons --with-keygrip --list-secret-keys
sec:u:4096:1:27304EDD6079B81C:1637342753:::u:::scESC:::+:::23::0:
fpr:::::::::88966A5B8C01BD04F3DA440427304EDD6079B81C:
grp:::::::::449972AC9FF11BCABEED8A7AE834C4349CC4DBFF:
uid:u::::1637342753::B3B0B2247600E80BAB9D4802D5CF0AFC477DE016::A committer <committer@example.com>::::::::::0:
ssb:u:4096:1:5B6BDD35BEDFBF6F:1637342753::::::e:::+:::23:
fpr:::::::::B1D4A2483D1D2A02416BE0775B6BDD35BEDFBF6F:
grp:::::::::97D36F5B8F5BECDA8A1923FC00D11C7C438584F9:

gpg --with-keygrip --list-secret-keys
sec   rsa4096 2021-11-19 [SC]
      88966A5B8C01BD04F3DA440427304EDD6079B81C
      Keygrip = 449972AC9FF11BCABEED8A7AE834C4349CC4DBFF
uid           [ultimate] A committer <committer@example.com>
ssb   rsa4096 2021-11-19 [E]
      Keygrip = 97D36F5B8F5BECDA8A1923FC00D11C7C438584F9
```

## Sample `gpg-agent` commands

Show agent config:

```shell
gpg-agent --gpgconf-list
```

## Sample `gpg-connect-agent` commands

Preset passphrase using `gpg-preset-passphrase`:

```shell
echo "$PASSPHRASE" | /usr/lib/gnupg2/gpg-preset-passphrase -v --preset $KEYGRIP
```

Preset passphrase using `gpg-connect-agent`:

```shell
gpg-connect-agent "PRESET_PASSPHRASE $KEYGRIP -1 $HEX_PASSPHRASE" /bye
```

How to preset passphrase to avoid GPG popup asking you for it:

- <https://www.gnupg.org/documentation/manuals/gnupg/Agent-PRESET_005fPASSPHRASE.html#Agent-PRESET_005fPASSPHRASE>
- <https://github.com/crazy-max/ghaction-import-gpg/blob/60f6f3e9a98263cc2c51ebe1f9babe82ded3f0ba/src/gpg.ts#L170-L174>

Prompt user for the passphrase:

```shell
gpg-connect-agent "GET_PASSPHRASE $KEYGRIP $ERROR $PROMPT $DESC" /bye
```

More info about [GET_PASSPHRASE command](https://www.gnupg.org/documentation/manuals/gnupg/Agent-GET_005fPASSPHRASE.html#Agent-GET_005fPASSPHRASE).

Get a list of the known keygrips:

```shell
gpg-connect-agent 'keyinfo --list' /bye
S KEYINFO 449972AC9FF11BCABEED8A7AE834C4349CC4DBFF D - - 1 P - - -
S KEYINFO 97D36F5B8F5BECDA8A1923FC00D11C7C438584F9 D - - - P - - -
OK
```

Show info about a key:

```shell
gpg-connect-agent "KEYINFO $KEYGRIP" /bye
S KEYINFO 449972AC9FF11BCABEED8A7AE834C4349CC4DBFF D - - 1 P - - -
OK
```

## Notes

[GiPython](https://github.com/gitpython-developers/GitPython) does not support commit signing directly:

Related issues:

- [Issue: How to gpg sign a commit?](https://github.com/gitpython-developers/GitPython/issues/580)
- [Issue: Can it generate signed commits and tags?](https://github.com/gitpython-developers/GitPython/issues/579)

## Links

About signing git commits:

- [Chris Reddington - Using GPG Keys to sign Git Commits - Part 3](https://www.cloudwithchris.com/blog/gpg-git-part-3/)
- [Benjamin Black - Signing Git commits with GPG keys that use modern encryption](https://dev.to/benjaminblack/signing-git-commits-with-modern-encryption-1koh)

About signing commits using subkeys:

- [Jente Hidskes - PSA: want to use a new subkey to sign your commits?](https://www.hjdskes.nl/blog/psa-github-gpg/)
- [Benjamin Black- Signing Git commits with GPG keys that use modern encryption](https://dev.to/benjaminblack/signing-git-commits-with-modern-encryption-1koh)
- [Signing commits in git uses wrong subkey](https://stackoverflow.com/questions/46330629/signing-commits-in-git-uses-wrong-subkey)

About using subkeys:

- [Using OpenPGP subkeys in Debian development](https://wiki.debian.org/Subkeys)
- [Andrew Matveychuk - How to sign your commits with GPG, Git and YubiKey](https://andrewmatveychuk.com/how-to-sign-you-commits-with-gpg-git-and-yubikey/)
- [Chris Reddington - Using GPG Keys to sign Git Commits - Part 2](https://www.cloudwithchris.com/blog/gpg-git-part-2)
- [Wil Clouser - Signing your commits on GitHub with a GPG key](https://micropipes.com/blog/2016/08/31/signing-your-commits-on-github-with-a-gpg-key/)
- [Benjamin Black - Signing Git commits with GPG keys that use modern encryption](https://dev.to/benjaminblack/signing-git-commits-with-modern-encryption-1koh)

GPG:

- [GPG Cheat Sheet](https://gock.net/blog/2020/gpg-cheat-sheet/)
- [GnuPG fingerprints, SSH fingerprints, and Keygrips](https://blog.djoproject.net/2020/05/03/main-differences-between-a-gnupg-fingerprint-a-ssh-fingerprint-and-a-keygrip/)

GPG and GitHub:

- [Generating a new GPG key](https://docs.github.com/en/authentication/managing-commit-signature-verification/generating-a-new-gpg-key)
- [Wil Clouser - Signing your commits on GitHub with a GPG key](https://micropipes.com/blog/2016/08/31/signing-your-commits-on-github-with-a-gpg-key/)
