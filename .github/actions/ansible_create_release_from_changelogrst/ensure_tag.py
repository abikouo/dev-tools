#!/usr/bin/python
# -*- coding: utf-8 -*-


from argparse import ArgumentParser
import requests
import sys

def main():
    parser = ArgumentParser()
    parser.add_argument("--repo", help="The repository name {owner}/{name}", required=True)
    parser.add_argument("--token", help="The Github token to use.", required=True)
    parser.add_argument("--tag", help="The tag to validate", required=True)

    args = parser.parse_args()
    url = f"https://api.github.com/repos/{args.repo}/tags"
    headers = {
      "Accept": "application/vnd.github+json",
      "Authorization": f"Bearer {args.token}",
      "X-GitHub-Api-Version": "2022-11-28",
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"GET url='{url}' => {response.status_code}")
    tags = [item.get("name") for item in response.json()]
    print(f"tags list {tags}")
    if args.tag not in tags:
        print(f"Tag '{args.tag}' not found from list {tags}")
        sys.exit(1)
    sys.exit(0)

if __name__ == "__main__":
    main()
