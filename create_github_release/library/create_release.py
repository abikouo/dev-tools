#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2023, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: create_release
short_description: Parse CHANGELOG.rst and create Github Release
author:
  - Aubin Bikouo (@abikouo)
description:
  - Parse CHANGELOG.rst for a specific release
  - Create Github Release
  - The module expects the Github token to be specified as GITHUB_TOKEN env variable
options:
  repository:
    description:
      - The repository name to create release on.
    required: true
    type: str
  tag:
    description:
      - The tag to release
    required: true
    type: str
  name:
    description:
      - The release name.
      - If not specified will be a combination of 'v' + I(tag)
    required: false
    type: str
"""

EXAMPLES = r"""
"""

RETURN = r"""
"""

import requests
import os
import re
from github import Github
from ansible.module_utils.basic import AnsibleModule


class CreateRelease(AnsibleModule):
    
    def __init__(self):

        argument_specs = dict(
            repository=dict(required=True),
            tag=dict(required=True),
            name=dict(),
        )

        super(CreateRelease, self).__init__(argument_spec=argument_specs, supports_check_mode=True)
        self.repository = self.params.get("repository")
        self.tag = self.params.get("tag")
        self.execute()
    
    def execute(self):

      gh_token = os.environ.get("GITHUB_TOKEN")
      if not gh_token:
          self.fail_json(msg="Please provide Github token using env variable 'GITHUB_TOKEN'")

      # Parse release content
      changelog_url = f"https://raw.githubusercontent.com/{self.repository}/main/CHANGELOG.rst"
      response = requests.get(changelog_url)
      if response.status_code != 200:
          self.fail_json(msg=f"Server returned [{response.status_code}] while trying to get '{changelog_url}'")
      data = response.text.splitlines()
      idx = 0
      start, end = -1, 0
      content = None
      while idx < len(data):
          if data[idx].startswith(f"v{self.tag}") and data[idx + 1] == "======":
              start = idx + 2
              idx += 2
          elif (
              start > 0
              and re.match(r"^v[0-9]+\.[0-9]+\.[0-9]+$", data[idx])
              and data[idx + 1] == "======"
          ):
              end = idx
              break
          idx += 1
      if start != -1:
          content = "\n".join(data[start:]) if not end else "\n".join(data[start:end])
      if not content:
          self.fail_json(msg=f"No content found into CHANGELOG.rst for release {self.tag}")
      # Create Github Release
      name = self.params.get("name") or f"v{self.tag}"
      if self.check_mode:
          self.exit_json(content=content, name=name, changed=True, msg=f"Would have created Github release {self.tag} if not in check_mode")
      gh_client = Github(gh_token)
      gh_repository = gh_client.get_repo(self.repository)
      gh_repository.create_git_release(self.tag, name, content)
      self.exit_json(changed=True, name=name, content=content)

def main():
    CreateRelease()

if __name__ == "__main__":
    main()