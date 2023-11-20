# Create Github Release

The following automation parse the content from the `CHANGELOG.rst` file and
create a release into Github repository

```shell
ansible-playbook ./play.yaml -e "@./vars.yaml" -v
```