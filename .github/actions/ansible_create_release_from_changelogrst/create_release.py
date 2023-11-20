#!/usr/bin/env python3
"""Script to read release content from CHANGELOG.rst file."""

import sys
import os
import re

from argparse import ArgumentParser
from pathlib import PosixPath

from github import Github


def create_git_release(
    repository: str, release_name: str, release_tag: str, release_content: str
) -> None:
    """Create github release on Repository.

    :param repository: Github repository name.
    :param release_tag: Release tag.
    :param release_content: Release description.
    :param release_name: The name of the release to create.
    """
    access_token = os.environ.get("GITHUB_TOKEN")

    gh_client = Github(access_token)
    gh_repository = gh_client.get_repo(repository)
    gh_repository.create_git_release(release_tag, release_name, release_content)


def parse_release_content(release_version: str) -> str:
    if not PosixPath("CHANGELOG.rst").exists():
        print("CHANGELOG.rst does not exist.")
        sys.exit(1)

    release_content = None
    with PosixPath("CHANGELOG.rst").open(encoding="utf-8") as file_write:
        data = file_write.read().splitlines()
        idx = 0
        start, end = -1, 0
        while idx < len(data):
            if data[idx].startswith(f"v{release_version}") and data[idx + 1] == "======":
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
            release_content = "\n".join(data[start:]) if not end else "\n".join(data[start:end])
    return release_content


def main() -> None:
    """Read release content from CHANGELOG.rst for a specific version."""
    parser = ArgumentParser(
        description="Read release content from CHANGELOG.rst for a specific version."
    )
    parser.add_argument("--repository", required=True, help="Repository name.")
    parser.add_argument("--tag", required=True, help="Release tag.")
    parser.add_argument("--name", help="Name of the release to create. default to v{tag}")

    args = parser.parse_args()

    release_content = parse_release_content(args.tag)
    if release_content:
        name = args.name or f"v{args.tag}"
        create_git_release(args.repository, name, args.tag, release_content)
    else:
        print("No release content found")
        sys.exit(1)


if __name__ == "__main__":
    main()
