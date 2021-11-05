## Sign automatic commits in GitHub Actions

WIP.

I'm working on a project where we use GitHub Actions intensively. One of the challenges we are facing is how we can sign commits when commits are created automatically from a GitHub Action. There is a lot of information about signing commits manually when the developer is creating the commit:

https://docs.github.com/en/authentication/managing-commit-signature-verification/signing-commits

but I have not found enough information about signing commits from bots and GitHub Actions. I have only found a couple of official pages from GitHub explaining how the commit signature works when using bots.

On the 15th of August 2019, GitHub published this very short article: [Commit signing support for bots and other GitHub Apps](https://github.blog/2019-08-15-commit-signing-support-for-bots-and-other-github-apps/)

The article points to the official documentation about [signature verification for bots](https://docs.github.com/en/authentication/managing-commit-signature-verification/about-commit-signature-verification#signature-verification-for-bots) where you can read:

> Signature verification for bots
>
> Organizations and GitHub Apps that require commit signing can use bots to sign commits. If a commit or tag has a bot signature that is cryptographically verifiable, GitHub marks the commit or tag as verified.
>
> Signature verification for bots will only work if the request is verified and authenticated as the GitHub App or bot and contains no custom author information, custom committer information, and no custom signature information, such as Commits API.

You can also find a link to the explanation about ["Authenticating as an installation"](https://docs.github.com/en/developers/apps/building-github-apps/authenticating-with-github-apps#authenticating-as-an-installation"). The whole documents refers to tokens that you can create for GitHub Apps. You can use those tokens in your GitHub Apps (bots) to access the GitHub API.

One of the things you can do with the API is to create a commit. So what they say is if you use a token generated for a bot (GitHub App) and you make a request to the API using that token (without custom author information), the GitHub API will recognize the bot token and will show the commit as verified.

So we can try to implement a solution using a token generated for a GitHub App.

## Solution 01: using the temporary GITHUB_TOKEN generated for each workflow job

What GitHub Apps authorization has to do with GitHub actions in a workflow?

As you can read on [GitHub docs](https://docs.github.com/en/actions/security-guides/automatic-token-authentication#about-the-github_token-secret) "at the start of each workflow run, GitHub automatically creates a unique GITHUB_TOKEN secret to use in your workflow. You can use the GITHUB_TOKEN to authenticate in a workflow run.". You can use that token to execute git commands and access the GitHub API too.

In fact, the token is generated for every job: "before each job begins, GitHub fetches an installation access token for the job. The token expires when the job is finished."

The [Checkout V2 GitHub Action](https://github.com/marketplace/actions/checkout) uses the token and persists it in the local git config. "This enables your scripts to run authenticated git commands. The token is removed during post-job cleanup".

So basically, you are provided with a kind of GitHub App token that you can use during the workflow execution.

You can use that token directly like this:

https://github.com/marketplace/actions/checkout#push-a-commit-using-the-built-in-token
```
on: push
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - run: |
          date > generated.txt
          git config user.name github-actions
          git config user.email github-actions@github.com
          git add .
          git commit -m "generated"
          git push
```

But the problem with that solution is the commit is not going to be signed. The other option is to use the token to make a request to the GitHub API to create the commit. There is an example in this repo using a GitHub API Python wrapper:

[01_sign_commit_using_github_api.py](./../src/01_sign_commit_using_github_api.py)

> WARNING: if you run the example locally using your own token the commit is not going to be signed. It only works when you use an app token. You can check the [workflow using this sample](./../.github/workflows/sample-01.yml).

Drawbacks for this solution:

* I have had problems with a 70MB file. The size limit for files in GitHub (without using LFS is 100MB).
* I have also had some timeouts.
* You have to deal with network latency, connection errors, etcetera in your workflow.
* If you make other git changes in your runner you end up changing the branch locally (runner) and remotely (API), and that could lead to a lot of merge conflicts.

The alternative solution could be to use your own PGP Key.

## Solution 02: using your own PGP Key as a secret

If you do not want to use the GITHUB_TOKEN you ca use your own GPG Key. For this example I'm not going to use the GiPython package becuase it seems it dnoes support commit signing directly. I'm going to use a GitHub Action that imports and sets up a GPG key in your workflow git configuration.

[sample-02.yml](./../.github/workflows/sample-02.yml)

First at all, you need a PGP key. I did not want to use my personal PGP key becuase it's going to be exposed as a repo secret. That means every mantainer (who can have access to the workflow) could sign a commit using my PGP Key. I have created a new GitHub account for this example (https://github.com/josecelano-bot) and I gave access to the bot to this repo.

Then, you only need to follow the steps on the [action documentation](https://github.com/marketplace/actions/import-gpg):

1. Export the Bot's PGP secret key:
```
gpg --armor --export-secret-key bot@josecelano.com -w0
```

2. Add the secrets to your repo: PGP secret key and passphrase

Does it make sense to use a shared PGP key? All mantainers will have access to the key. 

There is diffrenet proposal in a GitHub runner issue: https://github.com/actions/runner/issues/667#issuecomment-940441757

> The actual feature we should propose is to recognize myname+actions@github.com as a non-human account associated with me, and can be verified by my GPG keys. All I need is to store a private key as actions secret and use it for signing the commits.

If I understand the proposal, that means all automatic commits will be signed with the PGP key of the developer who triggered the workflow, just telling GitHub your PGP secret key and using an specific email for the commit author `josecelano+actions@github.com`. In the end, it's almost the same as creating your own bot account, but with two more advantages:

* You do not have to pay for an extra seat (depending on the GitHub licence you are using).
* You do not have to share that key with other mantainers.

## Notes

[GiPython](https://github.com/gitpython-developers/GitPython) does not support commit signing directly:
* https://github.com/gitpython-developers/GitPython/issues/580
* https://github.com/gitpython-developers/GitPython/issues/579

## Links

* [GitHub runner issue demanding signed commits for GitHub actions](https://github.com/actions/runner/issues/667)
* [Sign bot commit in actions, GitHub Community/](https://github.community/t/sign-bot-commit-in-actions/17896)
* [How to properly GPG-sign GitHub App (bot) created commits](https://github.community/t/how-to-properly-gpg-sign-github-app-bot-created-commits/131364)
* [Verified commits made easy with GitHub Actions](https://gist.github.com/swinton/03e84635b45c78353b1f71e41007fc7c)
* [GitHub Action to easily import a GPG key](https://github.com/marketplace/actions/import-gpg)