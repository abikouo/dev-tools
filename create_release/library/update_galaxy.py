#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2023, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: update_galaxy
short_description: Update galaxy file
author:
  - Aubin Bikouo (@abikouo)
description:
  - This module update the galaxy file while keeping all others information.
  - Running command like I(yq -yi '.version = "2.0.0"' galaxy.yml) do not preserve information like
    comments.
options:
  path:
    description:
      - The path to the collection where the galaxy file should be updated.
    type: path
    required: true
  version:
    description:
      - The version to set into the galaxy file.
    required: true
    type: str
"""

EXAMPLES = r"""
#Update galaxy file
- name: update version on galaxy file
  update_galaxy:
    path: /path/to/collection
    version: '2.0.0'
"""

RETURN = r"""
"""

import os

import ruamel.yaml

from ansible.module_utils.basic import AnsibleModule


def load_file(file):
    with open(file, 'r') as fh:
        data = fh.read()
        return ruamel.yaml.round_trip_load(data, preserve_quotes=True), any(d == "---" for d in data.split("\n"))


def dump_to_file(data, explicit_start, path):
    with open(path, 'w') as yaml_file:
        yaml = ruamel.yaml.YAML()
        yaml.preserve_quotes = True
        yaml.indent(mapping=2, sequence=4, offset=2)
        yaml.explicit_start = explicit_start
        yaml.dump(data, yaml_file)


class UpdateGalaxy(AnsibleModule):

    def __init__(self):
        
        specs = dict(
            path=dict(type="path", required=True,),
            version=dict(required=True,),
        )

        super(UpdateGalaxy, self).__init__(argument_spec=specs)
        self.version = self.params.get("version")

        found = False
        for suffix in ('yaml', 'yml'):
            self.path = os.path.join(self.params.get("path"), f"galaxy.{suffix}")
            if os.path.exists(self.path):
                found = True
                break
        if not found:
            self.fail_json(msg=f"Unable to locate galaxy file from path '{self.path}'.")
        self.execute()

    def execute(self):
        data, explicit_start = load_file(self.path)
        current = data.get("version")
        changed = False
        if current != self.version:
            data["version"] = self.version
            changed = True
            dump_to_file(data, explicit_start, self.path)

        self.exit_json(changed=changed)

def main():
    UpdateGalaxy()


if __name__ == "__main__":
    main()
