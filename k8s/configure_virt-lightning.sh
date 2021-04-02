#!/bin/bash

set -eux 

# install libvirt requirements using sudo
sudo yum install libvirt-devel libvirt-daemon-kvm libvirt-client
sudo systemctl enable --now libvirtd

# install virt-lightning requirements
pip install -r $(dirname $0)/requirements.txt

# get current user
local_user=$(whoami)

# do not prompt for virtualization
sudo usermod -a -G libvirt $local_user

# set permission
sudo mkdir -p /var/lib/virt-lightning/pool/upstream
sudo chown -R qemu:qemu /var/lib/virt-lightning/pool
sudo chmod 777 /var/lib/virt-lightning
sudo chmod 777 /var/lib/virt-lightning/pool /var/lib/virt-lightning/pool/upstream

# fetch fedora distribution
vl fetch fedora-33
