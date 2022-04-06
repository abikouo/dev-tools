#!/bin/bash

help()
{
   echo ""
   echo -e "Usage:\n\t$0 -m memory -d distribution -n vm_name"
   echo -e "Description:\n\tThis script is used to spawn/destroy a kubernetes cluster"
   echo "Options:"
   echo -e "\t-n : name of the vm name to create, default is kind-vm"
   echo -e "\t-m : memory used to create vm, default valut is '2000'"
   echo -e "\t-d : linux distribution. default is 'fedora-33'"
   echo -e "\t-k : if this flag is specified the running vm will be destroyed"
   exit 1
}

info(){
	echo    "-------------"
	echo -e "\033[0;35mInfo\033[0m: $1"
	echo    ""
}

warning(){
	echo    "-------------"
	echo -e "\033[0;33mWarning\033[0m: $1"
	echo    ""
}

error(){
	echo    "-------------"
	echo -e "\033[0;31mError\033[0m: $1"
	echo    ""
}

memory="2000"
linux_distro="fedora-33"
kill_vm=1

while getopts "n:m:d:k" opt
do
   case "$opt" in
      n ) vm_name="$OPTARG" ;;
      m ) memory="$OPTARG" ;;
      d ) linux_distro="$OPTARG" ;;
	  k ) kill_vm=0 ;;
      ? ) help ;; # Print helpFunction in case parameter is non-existent
   esac
done

if [ -z "$vm_name" ]; then 
	echo -e "\033[0;31merror: missing mandatory vm name\033[0m"
	help
fi

if [ "$kill_vm" == 0 ]; then
	info "Going to stop the following vm { $vm_name }"
	vl stop $vm_name
	exit 0
fi

# check if the distribution has already been fetched
info "check if { $linux_distro } has already been fetched" 
vl distro_list | grep $linux_distro > /dev/null
if [ $? -ne 0 ]; then 
	warning "$linux_distro is missing, we will try to fetch it"
	vl fetch $linux_distro
	if [ $? -ne 0 ]; then 
		error "unable to fetch distribution { $linux_distro }"
		exit 1
	fi
fi


set -eux
info "Start vm { name: '$vm_name', memory: '$memory', distro: '$linux_distro' }" 
vl start $linux_distro --memory $memory --name $vm_name

target=$(vl status | awk -v k="$vm_name" '{if($2==k){print $4;}}')
public_ip=$(awk -F "@" '{print $2}' <<< $target)
info "VM configuration { host: '$target', public_ip: '$public_ip' }" 

rc_file="/tmp/${vm_name}.k8s_config"


tmp_file="/tmp/configure_kube_cluster.sh"

echo "#!/bin/bash" > $tmp_file

echo "set -eu" >> $tmp_file
echo "curl -L -o /tmp/kubectl \"https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl\" " >> $tmp_file
echo "sudo mv /tmp/kubectl /usr/local/bin" >> $tmp_file

echo "echo \"kind: Cluster\" > /tmp/cluster_config.yaml" >> $tmp_file
echo "echo \"apiVersion: kind.x-k8s.io/v1alpha4\" >> /tmp/cluster_config.yaml" >> $tmp_file
echo "echo \"networking:\" >> /tmp/cluster_config.yaml" >> $tmp_file
echo "echo \"  apiServerAddress: $public_ip\" >> /tmp/cluster_config.yaml" >> $tmp_file
echo "echo \"  apiServerPort: 6443\" >> /tmp/cluster_config.yaml" >> $tmp_file


echo "sudo curl -Lo /usr/local/bin/kind https://kind.sigs.k8s.io/dl/v0.9.0/kind-linux-amd64" >> $tmp_file

echo "sudo chmod +x /usr/local/bin/kind /usr/local/bin/kubectl" >> $tmp_file

echo "sudo dnf -y --disablerepo updates install podman" >> $tmp_file
echo "sudo /usr/local/bin/kind create cluster --config /tmp/cluster_config.yaml" >> $tmp_file

echo "sudo kubectl create serviceaccount k8sadmin -n kube-system" >> $tmp_file
echo "sudo kubectl create clusterrolebinding k8sadmin --clusterrole=cluster-admin --serviceaccount=kube-system:k8sadmin" >> $tmp_file
echo "sudo kubectl create clusterrolebinding k8sadmin-view --clusterrole view --user k8sadmin" >> $tmp_file
echo "sudo kubectl create clusterrolebinding k8sadmin-secret-reader --clusterrole secret-reader --user k8sadmin" >> $tmp_file

echo "TOKENNAME=\$(sudo kubectl -n kube-system get serviceaccount/k8sadmin -o jsonpath='{.secrets[0].name}')" >> $tmp_file
echo "sudo kubectl -n kube-system get secret \$TOKENNAME -o jsonpath='{.data.token}'| base64 --decode > /tmp/k8sadmin-token-data" >> $tmp_file

scp $tmp_file $target:$tmp_file
rm -f $tmp_file

info "Configure cluster on vm"
ssh $target "chmod +x $tmp_file && $tmp_file"

echo "export K8S_AUTH_API_KEY=$(ssh $target cat /tmp/k8sadmin-token-data)" > $rc_file
echo export K8S_AUTH_VERIFY_SSL=False >> ${rc_file}
echo export K8S_AUTH_HOST=https://${public_ip}:6443 >> ${rc_file}

info "Full details for K8S configuration located here => {\033[0;32m${rc_file}\033[0m}"
