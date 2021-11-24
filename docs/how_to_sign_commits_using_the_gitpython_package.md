# How to sign commits using the GitPython package

> [GitPython](https://github.com/gitpython-developers/GitPython) is a python library used to interact with git repositories, high-level like git-porcelain, or low-level like git-plumbing.

TODO

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
