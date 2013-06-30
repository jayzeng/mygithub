from github3 import login
from git import *

import os
import sys
import subprocess
import argparse

class GitHubApiAuth(object):
    """
    Search for GitHub API token or password
    From either env or config
    """
    def get_token(self):
        return self._find_key()

    def _find_key(self):
        local_env = os.environ

        # Search for github keyword
        for key in local_env.iterkeys():
            if 'GITHUB' in key.upper():
                return local_env[key]

        # Look in config

        raise Exception('Please set GitHub API key (GITHUB_API_TOKEN) '\
                        'in environment or config')


class LocalRepo(object):
    def get_repo(self):
        """
        Returns an Repo instance
        """
        cwd = os.getcwd()
        return Repo(cwd, odbt=GitDB)

    def get_current_branch(self, repo):
        """
        Return current branch name

        Arg:
        repo - gitpython.Repo
        """
        return repo.active_branch.name

class Publish(object):
    def __init__(self, repo, current_branch):
        self.repo = repo
        self.current_branch = current_branch

    def parse_args(self):
        """
        Parse command line args
        """
        parser = argparse.ArgumentParser()
        parser.add_argument('-b', '--body', help='Pull request body (in markdown)', dest='body',required=True)
        parser.add_argument('-t', '--title', help='Pull request title', dest='title',required=True)
        parser.add_argument('--base', help='Base branch', dest='base',default='master')

        return parser.parse_args()

    def _send_pull(repo, title, head, base, body):
        """
        Creates a pull request

        args:
        title - pull request title
        head  - head brach
        base branch - base branch to be compared with (default to master)
        body  - pull request body

        raises Exception
        """
        created_pull = repo.create_pull(title, base, head, body=body)

        if created_pull:
            return created_pull.html_url

        # merge conflict
        raise Exception()

    def get_remote_info(self):
        remote_info = {}
        login_name = os.getlogin()

        for remote in self.repo.remotes:
            if login_name in remote.url:
                remote_info['remote_name'] = remote
                remote_url = remote.url
                remote_info['repo_name'] = remote_url.split('/')[1][:-4]
                remote_info['remote_url'] = remote_url
                break

        return remote_info

    def update_remote(self, origin_remote):
        return origin_remote.push(self.current_branch)

    def create_pull(self, token, repo_name, title, body, base_branch):
        """
        Creates a pull request on GitHub

        Args:
            token        - github api token
            repo_name    - local repository name
            title        - pull request title
            body         - pull request body (string or markdown)
            base_branch  - base branch, default to master
        Returns created pull request url
        """
        gh = login(token=token)

        # @TODO check github3.py to do a get repo instead of looping all repos
        repos = gh.iter_repos()

        for my_repo in repos:
            if repo_name == my_repo.name:
                # Retrieve pull request to ensure no pending pull request exists
                # for current branch
                pending_pulls = my_repo.iter_pulls()

                # @TODO see if GitHub API supports this operation. May be able to
                # avoid this check
                for pending_pull in pending_pulls:
                    pull_head = str(pending_pull.head)

                    # Return pending pull request url if current branch
                    # has an associated pull request
                    if self.current_branch in pull_head:
                        ret_msg = 'A pull request already exists for %s.\n' \
                                  'url: %s \n'  \
                                  'issue: %s \n' % (pull_head, pending_pull.issue_url, pending_pull.html_url)
                        return ret_msg

                # no pending pull requests
                try:
                    created_pull = my_repo.create_pull(title, base_branch, self.current_branch, body=body)

                    # created a pull request, returns url
                    if created_pull:
                        # open up pull request in browser
                        # @TODO add an option flag
                        subprocess.Popen(['open', html_url])
                        return created_pull.html_url
                except Exception,e:
                    if hasattr(e, 'errors'):
                        errors = e.errors.pop()
                        return errors['message']

                    return str(e)

def main():
    github_auth = GitHubApiAuth()
    api_token = github_auth.get_token()

    localRepo = LocalRepo()
    repo = localRepo.get_repo()
    current_branch = localRepo.get_current_branch(repo)

    # Don't allow master branch to create a pull request
    if current_branch == 'master':
        sys.exit('local branch can\'t be master')

    publish = Publish(repo, current_branch)
    publish_args = publish.parse_args()

    # Retrieve remote info
    remote_info = publish.get_remote_info()

    # Push current branch to remote
    publish.update_remote(remote_info['remote_name'])
    print('pushed to remote %s (%s)' % (remote_info['remote_name'], remote_info['remote_url']))

    print(publish.create_pull(api_token, remote_info['repo_name'], publish_args.title, publish_args.body, publish_args.base))

if __name__ == "__main__":
    main()
