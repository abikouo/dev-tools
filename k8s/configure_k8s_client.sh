#!/bin/bash

set -eux 

# install kubectl

curl -LO https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl

curl -LO https://storage.googleapis.com/kubernetes-release/release/v1.20.0/bin/linux/amd64/kubectl

chmod +x ./kubectl

sudo mv ./kubectl /usr/local/bin/kubectl

kubectl version --client

# install helm

helm_version="https://get.helm.sh/helm-v3.5.3-linux-amd64.tar.gz"

curl -LO ${helm_version}

tar -zxvf $(basename $helm_version)

sudo mv linux-amd64/helm /usr/local/bin/helm

rm -rf $(basename $helm_version) linux-amd64

# install python requirements for k8s
pip install -r $(dirname $0)/k8s_requirements.txt
