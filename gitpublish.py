#!/usr/bin/env python

from github3 import login
from git import Repo, GitDB

import os
import sys
import subprocess
import argparse

class GitHubApiAuth(object):
    def get_token(self):
        """
        Search for GitHub API token or password
        From either env or config
        """
        return self._find_key()

    def _find_key(self):
        """
        Locates api token from environment and/or local config
        """
        local_env = os.environ

        # Search for github keyword
        for key in local_env.iterkeys():
            if 'GITHUB' in key.upper():
                return local_env[key]

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
        """
        Args:
        repo  - gitpython.Repo local Repo instance
        current_branch - current git branch
        """
        self.repo = repo
        self.current_branch = current_branch

    def parse_args(self):
        """
        Parse command line args
        """
        parser = argparse.ArgumentParser()
        parser.add_argument('-b', '--body', help='Pull request body (in markdown)', dest='body')
        parser.add_argument('-t', '--title', help='Pull request title', dest='title')
        parser.add_argument('--base', help='Base branch', dest='base_branch', default='master')
        parser.add_argument('--in-browser', help='Open created pull request in browser', dest='in_browser', default='y')

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
        # @TODO This assumes user name is a substring of GitHub handle
        # Need to cover case like jay.zeng in local username
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
        """
        Arg
        origin_remote - your own remote (remote matched your username)
        """
        return origin_remote.push(self.current_branch)

    def create_pull(self, token, repo_name, cmd_args):
        """
        Creates a pull request on GitHub

        Args:
            token        - github api token
            repo_name    - local repository name
            cmd_args     - command line arguments
        Returns created pull request url
        """
        github_login = login(token=token)

        # @TODO check github3.py to do a get repo instead of looping all repos
        repos = github_login.iter_repos()

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
                    if not (cmd_args.title and cmd_args.body and cmd_args.base_branch):
                        sys.exit('Missing required arguments to create a pull request (title, body or base_branch)')

                    created_pull = my_repo.create_pull(cmd_args.title, cmd_args.base_branch,
                                                       self.current_branch, body=cmd_args.body)

                    # created a pull request, returns html url
                    if created_pull:
                        html_url = created_pull.html_url

                        # Open in browser?
                        if cmd_args.in_browser.lower() == 'y':
                            subprocess.Popen(['open', html_url])
                        return html_url
                except Exception,e:
                    if hasattr(e, 'errors'):
                        errors = e.errors.pop()
                        return errors['message']

                    return str(e)

def main():
    github_auth = GitHubApiAuth()
    api_token = github_auth.get_token()

    local_repo = LocalRepo()
    repo = local_repo.get_repo()
    current_branch = local_repo.get_current_branch(repo)

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

    print(publish.create_pull(api_token, remote_info['repo_name'], publish_args))

if __name__ == "__main__":
    main()
