# 🪣 Bitbucket Server PAT Generator

## 🤝 Introduction

[Bitbucket Server](https://www.atlassian.com/software/bitbucket/enterprise)
(nee [Stash](https://confluence.atlassian.com/bitbucketserver/bitbucket-rebrand-faq-779298912.html))
can hand out Personal Access Tokens (PAT) to be used in-place of user+password authentication.

When machine (rather than human) access to Stash is required, ideally it should be via short-lived credentials.  This
GitHub Action will take user+password credentials, and use them to generate a PAT.  You GitHub Actions workflow should
then use the PAT whenever authenticating to Stash.

**Wait. What?  🤔**

_Why would you use a PAT if you have a user+password already?_

Ideally this GitHub Action is used in conjunction with [Hashicorp Vault](https://www.vaultproject.io/), which will
automatically rotate the Stash user's password (e.g. using the
[AD secrets engine](https://www.vaultproject.io/docs/secrets/ad)).  This means during an execution of a (relatively 
long running) GitHub Actions workflow, the password could _change_ from the value originally obtained from Vault.

Obtaining a PAT allows us to avoid this issue, since the PAT will not be rotated (or used again).

**Not perfect**

This isn't the perfect way to go about getting a PAT from Stash for GitHub Actions when Vault is in the mix.  The ideal
solution is to create a new [Vault secrets engine](https://learn.hashicorp.com/tutorials/vault/plugin-backends) that
would connect to Stash directly and generate the PAT.  This would
simplify the implementation on the GitHub Actions side, since you could just use the Hashicorp Vault Action.

We have chosen not to create a new Vault secrets engine, as we could deliver this GitHub Action more quickly and simply
(as opposed to creating, building, publishing and installing a Vault plugin).

## 📄 Use

### ⌨️ Example

```yaml
      - name: Get creds from Vault
        id: vault
        uses: hashicorp/vault-action@v2.4.0
        with:
          url: https://vault.example.org/
          method: jwt
          exportEnv: false
          secrets: |
              ad/creds/svc_github_stash username | username ;
              ad/creds/svc_github_stash current_password | password

      - name: Get PAT for Stash
        id: stash
        uses: reecetech/bitbucket-server-pat-generator@2021.11.1
        with:
          url: https://stash.example.org/
          username: ${{ steps.vault.outputs.username }}
          password: ${{ steps.vault.outputs.password }}

      - name: Clone repo from Stash
        uses: reecetech/git-clone@2021.11.1
        with:
          url: https://stash.example.com/scm/example/repo.git
          username: ${{ steps.vault.outputs.username }}
          password: ${{ steps.stash.outputs.pat }}
```

### 📥 Inputs

🚧 To be completed

| name      | description                                               | required | default  |
| :---      | :---                                                      | :---     | :---     |

### 📤 Outputs

🚧 To be completed

| name            | description                                                        |
| :---            | :---                                                               |

## 💕 Contributing

Please raise a pull request, but note the testing tools below

### bats

BATS is used to test the logic of the shell scripts.

See: https://github.com/bats-core/bats-core

### shellcheck

Shellcheck is used to lint our shell scripts.

Please use [local ignores](https://stackoverflow.com/a/52659039) if you'd like to skip any particular checks.

See: https://github.com/koalaman/shellcheck
