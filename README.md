# Ignite
## Table of contents
[Introduction](#introduction)

[Architecture Overview](#architecture-overview)

[Build and Installation Procedure](#build-and-installation-procedure)

[Known Issues](#known-issues)

[Config Parameters](#config-parameters)

## Introduction:

Ignite is a highly functional end to end testing framework tool developed for 4G with the roadmap for 5G,which has flexibility to add protocols on need.  It is built on a generic mechanism to add protocols, messages as per need. Currently, it supports the basic 4G Protocols like S1AP, NAS-EMM, NAS-ESM, Diameter and GTP. It creates a API based mechanism for Testers to create test scripts and utlitize the protocol libraries to develop end to end functional scenarios.

## Architecture Overview:

![Image of Ignite Architecture](/Documentation/Images/ignite_architecture.jpg)


* S1AP Proxy (simulating eNodeB)
  - S1AP is a Application Layer protocol between eNodeB and MME, it runs on top of SCTP. S1AP messages encapsulates the NAS protocol(UEs payload). NAS protocol supports mobility management functionality and user plane bearer activation, modification and deactivation. It is also responsible of ciphering and integrity protection of NAS signaling. Data from eNodeB would be encoded by encapsulaing NAS message in proxy and sent to MME via SCTP. Once Data is received from MME, data would be decoded in proxy and sent to enodeB.
* UDP Proxy (simulating SGW)
  - MME communicates with SGW over S11 protocol using GTP-C protocol. This protocol tunnels signaling messages between MME and S-GW. GTP-C runs on top of UDP.Data from SGW would be encoded in proxy and sent to MME via UDP. Once Data is received from MME, data would be decoded in proxy and sent to SGW.
* Diameter Proxy(simulating HSS)
  - MME communicates with HSS over S6a interface using Diameter protocol.This protocol supports transferring of subscription and authentication data for authenticating/authorizing user access to the evolved system between MME and HSS. Data from Diameter would be encoded in proxy and sent to MME via SCTP. Once Data is received from MME, data would be decoded in proxy and sent to Diameter

Default Message Templates for each interface to be used in the test scenario. These default message templates are created using JSON. Messages are sent/received to and from proxy and MME via REST APIs. Messages received are having basic validations done implict both explicit. This framework provides flexibility to develop test cases using Python and ROBO Framework. MME Logs, Pcaps and ignite logs are collected from ROBOT Framework. GRPC commands are executed to check the statistics after every attach and detach.

## Build and Installation Procedure

## Deploy Ignite in Kubernetes Environment

### Install Kubernetes

Before deploying Ignite, Execute below commands to install kubernetes with kubespray.

```
# Download Kubespray
cd ${HOME}
git clone https://github.com/kubernetes-incubator/kubespray.git -b release-2.11

# Create Python virtual environment for Kubespray
sudo apt update
sudo apt install -y software-properties-common python-pip
sudo pip install virtualenv
virtualenv ${HOME}/venv/ciab
source ${HOME}/venv/ciab/bin/activate

# Run Kubespray
cd ${HOME}/kubespray
pip install -r requirements.txt
ansible-playbook -b -i inventory/local/hosts.ini \
		-e "{'override_system_hostname' : False, 'disable_swap' : True}" \
		-e "{'docker_version' : 18.09}" \
		-e "{'docker_iptables_enabled' : True}" \
		-e "{'kube_version' : v1.15.3}" \
		-e "{'kube_network_plugin_multus' : True, 'multus_version' : stable}" \
		-e "{'kube_proxy_metrics_bind_address' : 0.0.0.0:10249}" \
		-e "{'kube_pods_subnet' : 192.168.0.0/17, 'kube_service_addresses' : 192.168.128.0/17}" \
		-e "{'skydns_server' : 192.168.128.3}" \
		-e "{'kube_apiserver_node_port_range' : 2000-36767}" \
		-e "{'kubeadm_enabled': True}" \
		-e "{'kube_feature_gates' : [SCTPSupport=True]}" \
		-e "{'kubelet_custom_flags' : [--allowed-unsafe-sysctls=net.*]}" \
		-e "{'dns_min_replicas' : 1}" \
		-e "{'helm_enabled' : True, 'helm_version' : v2.16.1}" \
    cluster.yml
deactivate

# Copy the cluster config to user home
mkdir -p ${HOME}/.kube
sudo cp -f /etc/kubernetes/admin.conf ${HOME}/.kube/config
sudo chown $(id -u):$(id -g) ${HOME}/.kube/config

# Init Helm and add additional Helm repositories
helm init --wait --client-only
helm repo add incubator https://kubernetes-charts-incubator.storage.googleapis.com/
helm repo add cord https://charts.opencord.org
```

Note: The coreDNS service (kubectl get services -n kube-system) is assigned an ip address of x.x.x.3
by the kubespray playbook. However the coreDNS ip in config is set as  x.x.x.10. This has to be
changed to .3 in the below file once the playbook is completed:
	sudo vi /var/lib/kubelet/config.yaml
	sudo systemctl restart kubelet

### Create Docker Image

Below command will create Ignite docker image.

	cd {install_path}/ignite
	sudo make docker-build

### Delpoy Helm Chart

Below command would deploy the Ignite docker image in four containers and start Diameter, S1AP and GTP proxies.

	cd {install_path}/ignite/Deployment
	sudo helm upgrade --install ignite ignite --namespace omec

Note: Ignite containers will come up only when MME containers are up and running. MME containers to be brought up, before starting the Ignite containers.

### Execute Test Cases

Enter in to runtestcase container using below command

	sudo kubectl exec -it ignite-0 -n omec -c runtestcase -- bash

To execute single test case use as below ,

* Python TC 
	```
	./ignite-run.sh LTE_4G_Setup.py
	./ignite-run.sh LTE_4G_IMSIAttachDetach.py
	```
* ROBO TC
	```
	./ignite-run.sh 4G_Attach_Setup_Request.robot
	./ignite-run.sh 4G_Attach.robot
	```
To execute test case as package use as below,

* Python TC 
	```
	./ignite-run.sh pythonregressionpkg
	./ignite-run.sh pythonsanitypkg
	```
	
* ROBO TC
	```
	./ignite-run.sh roboregressionpkg
	./ignite-run.sh robosanitypkg
	```
	
## Deploy Ignite in Non Kubernetes Environment

To start Ignite in a non Kubernetes environment, update and start as below,

### Update config 

Update following config files
    {install_path}/ignite/Dev/Common/configuration.json

### Start Ignite proxies
##### Diameter Proxy
	cd {install_path}/ignite/Dev/Protocol/Diameter
	python3 diameterProxy.py

##### S1AP Proxy
	cd {install_path}/ignite/Dev/Protocol/S1AP
	python3 s1apProxy.py

##### GTP Proxy
	cd {install_path}/ignite/Dev/Protocol/GTP
	python3 udpProxy.py

## Known Issues

Click on the [Link to Known Issues](/Documentation/known-issues.txt) to access list of known issues

## Appendix A.
Before starting Ignite proxies respective parameters should be configured in the json files mentioned in below table.
Below parameters needs to be modified on all three protocols(s1ap,gtp,diameter), as Ignite is designed modulerly to start proxies from different VM/host.
After configuration changes, OMEC-MME should should be started first, then Diameter Proxy, S1AP Proxy and GTP Proxy should be started

### Config Parameters
- Following is a description of each section under json file.
  - [U] - Reserved/Unused. Can be skipped in the json.
  - [M] - Mandatory parameter.
  
#### "configuration" - Contains information relevant for S1AP, GTP and Diameter.
  Config Parameter Name | Reserved/Unused/Mandatory | Comments |
  ----------------------|---------------------------|----------|
  sut_ip     | Mandatory                    | OMEC-MME IP Address |
  ignite_ip               | Mandatory                 | Ignite IP address. |
