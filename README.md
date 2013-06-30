mygithub
========

My GitHub productivity scripts

git publish  - publish current branch to GitHub and creates a pull request

## Help & Usage
If you already have a GitHub API token, you can set it as environment variable.
(See "Personal API Access Tokens" in https://github.com/settings/applications)

```bash
export GITHUB_API_TOKEN=<my-token>
```


```bash
usage: git_publish.py [-h] -b BODY -t TITLE [--base BASE]

optional arguments:
  -h, --help            show this help message and exit
  -b BODY, --body BODY  Pull request body (in markdown)
  -t TITLE, --title TITLE
                        Pull request title
  --base BASE           Base branch
```

## Example
To create a new pull request
```bash
python git_publish.py -t 'gitignore' -b '## Check in gitignore'
```

If a pull request already exists:
```bash
[jayzeng] ~/Projects/mygithub] (prototype/publish)>  python git_publish.py
pushed to remote origin (git@github.com:jayzeng/mygithub.git)
A pull request already exists for <Head [jayzeng:prototype/publish]>.
url: https://github.com/jayzeng/mygithub/issues/2
issue: https://github.com/jayzeng/mygithub/pull/2
```

## Dependencies
- GitPython (https://github.com/gitpython-developers/GitPython)
- github3.py (https://github.com/sigmavirus24/github3.py)
