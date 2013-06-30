mygithub
========

My GitHub productivity scripts

git publish  - publish current branch to GitHub and creates a pull request

## Help & Usage
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
```bash
python git_publish.py -t 'gitignore' -b '## Check in gitignore'
```
