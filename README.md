# 🪣 Bitbucket Server PAT Generator

⚠️ **No longer updated - **reece**tech no longer uses Bitbucket server, making maintance of this action difficult to verify - feel free to fork**

## 🤝 Introduction

[Bitbucket Server](https://www.atlassian.com/software/bitbucket/enterprise)
(nee [Stash](https://confluence.atlassian.com/bitbucketserver/bitbucket-rebrand-faq-779298912.html))
can hand out Personal Access Tokens (PAT) to be used in-place of user+password authentication.

When machine (rather than human) access to Stash is required, ideally it should be via short-lived credentials.  This
GitHub Action will take user+password credentials, and use them to generate a PAT.  Your GitHub Actions workflow should
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

## ⌨️ Example

```yaml
      - name: Get creds from Vault
        id: vault
        uses: hashicorp/vault-action@v2.4.3
        with:
          url: https://vault.example.org/
          method: jwt
          exportEnv: false
          secrets: |
              ad/creds/svc_github_stash username | username ;
              ad/creds/svc_github_stash current_password | password

      - name: Get PAT for Stash
        id: stash
        uses: reecetech/bitbucket-server-pat-generator@2022.11.5
        with:
          base_url: https://stash.example.org/
          username: ${{ steps.vault.outputs.username }}
          password: ${{ steps.vault.outputs.password }}

      - name: Clone repo from Stash
        uses: example/git-clone
        with:
          url: https://stash.example.com/scm/example/repo.git
          username: ${{ steps.vault.outputs.username }}
          password: ${{ steps.stash.outputs.pat }}
```

## Inputs

<!-- AUTO-DOC-INPUT:START - Do not remove or modify this section -->

|          INPUT           |  TYPE  | REQUIRED |             DEFAULT              |                                                                                                                                      DESCRIPTION                                                                                                                                       |
|--------------------------|--------|----------|----------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
|         base_url         | string |   true   |                                  |                                                                                                                            Base URL of Bitbucket Server<br>                                                                                                                            |
|  check_using_ldap_bind   | string |  false   |            `"false"`             |                                                                          Check the password validity using<br>an LDAP bind to avoid<br>Bitbucket requiring a CAPTCHA after<br>failed authentication attempts                                                                           |
|        ldap_hosts        | string |  false   |                                  |                                                                                               Comma separated list of LDAP<br>hosts (only used if `check_using_ldap_bind`<br>is `true`)                                                                                                |
|        ldap_path         | string |  false   |                                  | The path where the username<br>will be found in the<br>LDAP tree (only used if<br>`check_using_ldap_bind` is `true`) For example,<br>if the user object is<br>`CN=username,OU=tech,OU=Accounts,DC=example,DC=org`, then set `ldap_path` to:<br>`OU=tech,OU=Accounts,DC=example,DC=org` |
|        ldap_port         | string |  false   |             `"389"`              |                                                                                                TCP port to connect to<br>LDAP hosts (only used if<br>`check_using_ldap_bind` is `true`)                                                                                                |
|       max_attempts       | string |  false   |              `"10"`              |                                                                                                                    Number of times to attempt<br>to generate a PAT                                                                                                                     |
|           mode           | string |  false   |            `"create"`            |                                                                                                                    Mode to run in -<br>either `create` or `revoke`                                                                                                                     |
|         password         | string |   true   |                                  |                                                                                                                       Password to connect to Bitbucket<br>Server                                                                                                                       |
|          pat_id          | string |  false   |                                  |                                                                                                          The ID of the PAT<br>to revoke (only used if<br>`mode` is `revoke`)                                                                                                           |
|         pat_uri          | string |  false   | `"rest/access-tokens/1.0/users"` |                                                                                                                          The REST endpoint for PAT<br>actions                                                                                                                          |
|   project_permissions    | string |  false   |            `"write"`             |                                                                                                                      Project permissions: read, write or<br>admin                                                                                                                      |
|  repository_permissions  | string |  false   |            `"write"`             |                                                                                                                    Repository permissions: read, write or<br>admin                                                                                                                     |
| seconds_between_attempts | string |  false   |              `"30"`              |                                                                                                           Number of seconds to wait<br>before retrying to generate a<br>PAT                                                                                                            |
|         username         | string |   true   |                                  |                                                                                                                       Username to connect to Bitbucket<br>Server                                                                                                                       |
|        valid_days        | string |  false   |              `"1"`               |                                                                                                                             Days the PAT will be<br>valid                                                                                                                              |

<!-- AUTO-DOC-INPUT:END -->

## Outputs

<!-- AUTO-DOC-OUTPUT:START - Do not remove or modify this section -->

|      OUTPUT      |  TYPE  |                DESCRIPTION                 |
|------------------|--------|--------------------------------------------|
|       pat        | string |   PAT to connect to Bitbucket<br>Server    |
|   pat_encoded    | string |              PAT URL encoded               |
|      pat_id      | string |  ID of the PAT (can<br>be used to revoke)  |
|     username     | string | Username to connect to Bitbucket<br>Server |
| username_encoded | string |            Username URL encoded            |

<!-- AUTO-DOC-OUTPUT:END -->

## 💕 Contributing

Please raise a pull request, but note the testing tools below

### pylint

pylint is used to lint the Python code

See: https://pylint.org/
