#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2023, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: ensure_tag
short_description: Ensure a specified tag exists into Github repository
author:
  - Aubin Bikouo (@abikouo)
description:
  - Ensure a specific tag is present in a Github repository.
  - The module expects the GITHUB_TOKEN to be set as environment variable
options:
  repository:
    description:
      - The repository name.
    required: true
  tag:
    description:
      - The tag to validate.
    required: true
    type: str
"""

EXAMPLES = r"""
"""

RETURN = r"""
"""

import os
import requests
from ansible.module_utils.basic import AnsibleModule


class EnsureTag(AnsibleModule):

    def __init__(self):
        
        specs = dict(
            tag=dict(required=True),
            repository=dict(required=True),
        )

        super(EnsureTag, self).__init__(argument_spec=specs)
        self.tag = self.params.get("tag")
        self.repo = self.params.get("repository")
        self.execute()

    def execute(self):
      
      gh_token = os.environ.get("GITHUB_TOKEN")
      if not gh_token:
          self.fail_json(msg="Please provide Github token using env variable 'GITHUB_TOKEN'")
      tag_url = f"https://api.github.com/repos/{self.repo}/tags"
      headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {gh_token}",
        "X-GitHub-Api-Version": "2022-11-28",
      }

      response = requests.get(tag_url, headers=headers)
      if response.status_code != 200:
          self.fail_json(msg=f"Server responds {response.status_code} while trying to retrieve tags")
      
      tags = [item.get("name") for item in response.json()]
      self.exit_json(exists=(self.tag in tags), tags=tags)

def main():
    EnsureTag()


if __name__ == "__main__":
    main()
