#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2023, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: compute_release_params
short_description: Compute releasing parameters
author:
  - Aubin Bikouo (@abikouo)
description:
  - Determines the upstream branch name and the fork branch name.
options:
  repository:
    description:
      - The repository name to validate.
    required: true
    type: str
  version:
    description:
      - The release version to validate.
    required: true
    type: str
"""

EXAMPLES = r"""
"""

RETURN = r"""
"""

from ansible.module_utils.basic import AnsibleModule
from packaging import version
import os
import re


class ComputeReleaseParams(AnsibleModule):
    
    def __init__(self):
        
        specs = dict(
            repository=dict(required=True),
            version=dict(required=True),
        )

        super(ComputeReleaseParams, self).__init__(argument_spec=specs)
        self.repository = self.params.get("repository")
        self.version = self.params.get("version")
        self.execute()

    def validate_version(self):
        try:
            self.v = version.Version(self.version)
        except version.InvalidVersion as e:
            self.fail_json(msg=str(e))

    def validate_repository(self):
        repo = self.repository.replace("https://github.com/", "")
        if len(repo.split("/")) != 2:
            self.fail_json(msg=f"Wrong format for repository name {self.repository}")
        self.repo_org = repo.split("/")[0]
        self.repo_name = repo.split("/")[1]

    def read_github_credentials(self):

        gitcredentials_file = os.path.expanduser('~/.git-credentials')
        if not os.path.exists(gitcredentials_file):
            self.fail_json(msg=f"unable to determine git credentials, the following file does not exists '{gitcredentials_file}'")

        with open(gitcredentials_file) as f:
            d = f.read()
            m = re.match('^https://(.*)\:(.*)@github.com$', d)
            if not m:
                self.fail_json(msg=f"invalid format for git credentials file {gitcredentials_file}")
            return m.group(1), m.group(2)

    def execute(self):

        self.validate_version()
        self.validate_repository()
        github_user, github_token = self.read_github_credentials()
        self.exit_json(
            changed=False,
            github_user=github_user,
            github_token=github_token,
            github_fork=f"https://github.com/{github_user}/{self.repo_name}",
            github_upstream=f"https://github.com/{self.repo_org}/{self.repo_name}",
            stable_branch=f"stable-{self.v.major}.{self.v.minor}",
            release_branch=f"prepare_release_{self.version}",
        )

def main():
    ComputeReleaseParams()


if __name__ == "__main__":
    main()
