# How to prepare release

Update the ``vars.yaml`` file in this repository.
The playbook excepts git credentials to be stored into ``~/.git-credentials``, you can create this file by running
``git config credential.helper store`` in a git repository.
 
Run using the following command: 

```shell
ansible-playbook ./play.yaml -e "@./vars.yaml" -v
```