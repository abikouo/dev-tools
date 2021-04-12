#!/bin/bash

set -eux

file=$1

server=$(cat $file | awk '{ print $2 }' | grep "K8S_AUTH_HOST" | cut -d '=' -f2)
apikey=$(cat $file | awk '{ print $2 }' | grep "K8S_AUTH_API_KEY" | cut -d '=' -f2)


kubectl config set-cluster dev_0 --server="${server}" --insecure-skip-tls-verify
kubectl config set-credentials user_0 --token="${apikey}"
kubectl config set-context ansible --cluster=dev_0 --user=user_0
kubectl config view
kubectl config use-context ansible
