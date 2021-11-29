# How to create a subkey for signing

After reading this [article about GPG subkeys](https://wiki.debian.org/Subkeys), I realized that using only the primary GPG key to sign commits is not probably a good idea.

If you want to sign commits and you do not know how to do it, you will probably end up reading Git or GitHub official documentation:

- [Git Documentation - Git Tools - Signing Your Work](https://git-scm.com/book/en/v2/Git-Tools-Signing-Your-Work)
- [GitHub Documentation - Signing commits](https://docs.github.com/en/authentication/managing-commit-signature-verification/signing-commits)

In those documents, they promote the use of the master or primary key. Or at least, it's what they use. They probably do not want to overwhelm the reader with a lot of GPG technical stuff.

If you list one of your GPG keys you will see something like:

```text
gpg --list-keys --fingerprint --with-keygrip --with-subkey-fingerprints 88966A5B8C01BD04F3DA440427304EDD6079B81C
pub   rsa4096 2021-11-19 [SC]
      8896 6A5B 8C01 BD04 F3DA  4404 2730 4EDD 6079 B81C
      Keygrip = 449972AC9FF11BCABEED8A7AE834C4349CC4DBFF
uid           [ultimate] A committer <committer@example.com>
sub   rsa4096 2021-11-19 [E]
      B1D4 A248 3D1D 2A02 416B  E077 5B6B DD35 BEDF BF6F
      Keygrip = 97D36F5B8F5BECDA8A1923FC00D11C7C438584F9
```

The meaning for the letters inside brackets are the [GPG key capabilities](https://github.com/gpg/gnupg/blob/master/doc/DETAILS#field-12---key-capabilities):

| Character | Capability |
| ------------- | ------------- |
| S  | Sign |
| C   | Certify |
| E   | Encrypt |
| A   | Authentication |

If you want to create a signing key, you can follow [Debian's post](https://wiki.debian.org/Subkeys). In my case for the key I'm using in all the examples, this was the output:

```text
gpg --edit-key 88966A5B8C01BD04F3DA440427304EDD6079B81C

gpg (GnuPG) 2.2.19; Copyright (C) 2019 Free Software Foundation, Inc.
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.

Secret key is available.

sec  rsa4096/27304EDD6079B81C
     created: 2021-11-19  expires: never       usage: SC  
     trust: ultimate      validity: ultimate
ssb  rsa4096/5B6BDD35BEDFBF6F
     created: 2021-11-19  expires: never       usage: E   
[ultimate] (1). A committer <committer@example.com>

gpg> addkey
Please select what kind of key you want:
   (3) DSA (sign only)
   (4) RSA (sign only)
   (5) Elgamal (encrypt only)
   (6) RSA (encrypt only)
  (14) Existing key from card
Your selection? 4
RSA keys may be between 1024 and 4096 bits long.
What keysize do you want? (3072) 4096
Requested keysize is 4096 bits
Please specify how long the key should be valid.
         0 = key does not expire
      <n>  = key expires in n days
      <n>w = key expires in n weeks
      <n>m = key expires in n months
      <n>y = key expires in n years
Key is valid for? (0) 
Key does not expire at all
Is this correct? (y/N) y
Really create? (y/N) y
We need to generate a lot of random bytes. It is a good idea to perform
some other action (type on the keyboard, move the mouse, utilize the
disks) during the prime generation; this gives the random number
generator a better chance to gain enough entropy.

sec  rsa4096/27304EDD6079B81C
     created: 2021-11-19  expires: never       usage: SC  
     trust: ultimate      validity: ultimate
ssb  rsa4096/5B6BDD35BEDFBF6F
     created: 2021-11-19  expires: never       usage: E   
ssb  rsa4096/3F39AA1432CA6AD7
     created: 2021-11-26  expires: never       usage: S   
[ultimate] (1). A committer <committer@example.com>

gpg> save
```

If I list again the key:

```text
gpg --list-keys --fingerprint --with-keygrip --with-subkey-fingerprints 88966A5B8C01BD04F3DA440427304EDD6079B81C
pub   rsa4096 2021-11-19 [SC]
      8896 6A5B 8C01 BD04 F3DA  4404 2730 4EDD 6079 B81C
      Keygrip = 449972AC9FF11BCABEED8A7AE834C4349CC4DBFF
uid           [ultimate] A committer <committer@example.com>
sub   rsa4096 2021-11-19 [E]
      B1D4 A248 3D1D 2A02 416B  E077 5B6B DD35 BEDF BF6F
      Keygrip = 97D36F5B8F5BECDA8A1923FC00D11C7C438584F9
sub   rsa4096 2021-11-26 [S]
      BD98 B3F4 2545 FF93 EFF5  5F7F 3F39 AA14 32CA 6AD7
      Keygrip = 00CB9308AE0B6DE018C5ADBAB29BA7899D6062BE
```

Then, you can replace your git config:

```text
[user]
        name = Your Name
        email = your@email.com
        signingkey = B29BA7899D6062BE
```

You need to upload again the public key to GitHub to import also the subkey, otherwise you new commits using the subkey will be shown as unverified.

You should remove all the capabilities from the primary key except for "Certify" ([C]). You can do it by editing the primary key in expert mode. You have to use the option `change-usage` which is a "hidden" option (not listed with the `help` command)

```shell
gpg --expert --edit-key 88966A5B8C01BD04F3DA440427304EDD6079B81C
gpg (GnuPG) 2.2.19; Copyright (C) 2019 Free Software Foundation, Inc.
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.

Secret key is available.

sec  rsa4096/27304EDD6079B81C
     created: 2021-11-19  expires: never       usage: SC  
     trust: ultimate      validity: ultimate
ssb  rsa4096/5B6BDD35BEDFBF6F
     created: 2021-11-19  expires: never       usage: E   
ssb  rsa4096/3F39AA1432CA6AD7
     created: 2021-11-26  expires: never       usage: S   
[ultimate] (1). A committer <committer@example.com>

gpg> change-usage
Changing usage of the primary key.

Possible actions for a RSA key: Sign Certify Encrypt Authenticate 
Current allowed actions: Sign Certify 

   (S) Toggle the sign capability
   (E) Toggle the encrypt capability
   (A) Toggle the authenticate capability
   (Q) Finished

Your selection? S

Possible actions for a RSA key: Sign Certify Encrypt Authenticate 
Current allowed actions: Certify 

   (S) Toggle the sign capability
   (E) Toggle the encrypt capability
   (A) Toggle the authenticate capability
   (Q) Finished

Your selection? Q

sec  rsa4096/27304EDD6079B81C
     created: 2021-11-19  expires: never       usage: C   
     trust: ultimate      validity: ultimate
ssb  rsa4096/5B6BDD35BEDFBF6F
     created: 2021-11-19  expires: never       usage: E   
ssb  rsa4096/3F39AA1432CA6AD7
     created: 2021-11-26  expires: never       usage: S   
[ultimate] (1). A committer <committer@example.com>

gpg> save
```

After editing the key you should see only the `[C]` capability on the primary key.

```shell
gpg -k
/home/josecelano/.gnupg/pubring.kbx
-----------------------------------
pub   rsa4096 2021-11-19 [C]
      88966A5B8C01BD04F3DA440427304EDD6079B81C
uid           [ultimate] A committer <committer@example.com>
sub   rsa4096 2021-11-19 [E]
sub   rsa4096 2021-11-26 [S]
```

## Links

- [Using OpenPGP subkeys in Debian development](https://wiki.debian.org/Subkeys)

- [Create GnuPG key with sub-keys to sign, encrypt, authenticate](https://blog.tinned-software.net/create-gnupg-key-with-sub-keys-to-sign-encrypt-authenticate/)
- [Generate GPG Master and Subkeys](https://blog.programster.org/generating-gpg-master-and-subkeys)
- [GPG - Subkeys](https://blog.programster.org/gpg-subkeys)
- [GPG Subkeys](https://oguya.ch/posts/2016-04-01-gpg-subkeys/)
- [Creating a new GPG key with subkeys](https://www.void.gr/kargig/blog/2013/12/02/creating-a-new-gpg-key-with-subkeys/)
- [Generating More Secure GPG Keys: Rationale](https://spin.atomicobject.com/2013/10/23/secure-gpg-keys/)
