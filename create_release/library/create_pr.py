#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2023, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: create_pr
short_description: Create pull request on Github repository
author:
  - Aubin Bikouo (@abikouo)
description:
  - Create pull request using input parameters
options:
  repository:
    description:
      - The repository for the pull request to create.
    required: true
    type: str
  base:
    description:
      - The base branch.
    required: true
    type: str
  head:
    description:
      - The head branch.
      - When creating from fork should be specified as 'owner:branch'
    required: true
    type: str
  body:
    description:
      - The pull request body.
    required: true
  title:
    description:
      - The pull request title.
    required: true
  token:
    description:
      - The Github token used to create pull request.
    required: true
    no_log: true
"""

EXAMPLES = r"""
"""

RETURN = r"""
"""

from github import Github
from github import GithubException
from ansible.module_utils.basic import AnsibleModule


class CreatePR(AnsibleModule):
    
    def __init__(self):

        argument_specs = dict(
            repository=dict(required=True),
            base=dict(required=True),
            head=dict(required=True),
            title=dict(required=True),
            body=dict(required=True),
            token=dict(required=True, no_log=True),
        )

        super(CreatePR, self).__init__(argument_spec=argument_specs)
        self.execute()

    def execute(self):

        try:
            client = Github(self.params.get("token"))
            repo = client.get_repo(self.params.get("repository"))

            params = {
                "title": self.params.get("title"),
                "body": self.params.get("body"),
                "base": self.params.get("base"),
                "head": self.params.get("head"),
            }

            pr = repo.create_pull(**params)
            self.exit_json(changed=True, url=pr.html_url, id=pr.id, commits=pr.commits, changed_files=pr.changed_files)

        except GithubException as err:
            if err.status == 422 and "A pull request already exists" in str(err):
                self.exit_json(changed=False, msg=err.data.get("errors")[0]["message"])
            self.fail_json(msg="Failed to create pull request due to: %s" % str(err.data.get("errors")))

        except Exception as e:
            self.fail_json(msg="An error occurred while regenerating collection", exception=e)



def main():
    CreatePR()

if __name__ == "__main__":
    main()