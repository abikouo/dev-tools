# Kubernetes

This fragment hosts all tools related to kubernetes sdk

## spawn_k8s_cluster.sh

This tool will create a kubernetes cluster on a vm spawned using the virt-lightning python module
You should install first the python requirements using: 

```
./configure_virt-lightning.sh
```
This will basically install virt-lighning module use to spawn the vm.

Then the tool can be run using the following syntax: 

```
spawn_k8s_cluster.sh -n vm_name
```


## configure kubernetes and openshift local client

using the following command: 

```
configure_k8s_client.sh
```

This will basically install the ``kubectl`` executable on the local user path and 
install kubernetes/openshift ansible requirements.

