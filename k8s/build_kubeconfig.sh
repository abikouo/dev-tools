#!/bin/bash

set -eux

file=$1
kube_config="$HOME/.kube/config"

if [ "$#" -ne 1 ]; then
	kube_config=$2
fi

server=$(cat $file | awk '{ print $2 }' | grep "K8S_AUTH_HOST" | cut -d '=' -f2)
apikey=$(cat $file | awk '{ print $2 }' | grep "K8S_AUTH_API_KEY" | cut -d '=' -f2)

kubectl config set-cluster dev_0 --server="${server}" --insecure-skip-tls-verify --kubeconfig ${kube_config}
kubectl config set-credentials user_0 --token="${apikey}" --kubeconfig ${kube_config}
kubectl config set-context ansible --cluster=dev_0 --user=user_0  --kubeconfig ${kube_config}
kubectl config view --kubeconfig ${kube_config}
kubectl config use-context ansible --kubeconfig ${kube_config}
