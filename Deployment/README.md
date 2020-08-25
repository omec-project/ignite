**Steps:**

1.  make migsetup
    
    This sets up the kubernetes cluster using the tools provided by kubespray.
    
2.  Clone ignite source code, build the docker image
    docker build -t omec-project/ignite:1.0.0 -f dockerfile .
    
3.  Clone MME source code, build the MME docker image
    sudo docker-build

4.  Update image name in values.yaml file in omec-mme helm-chart

5.  make migutbox

    This installs the omec-mme helm-chart, bringing up the ignite and mme pods in omec namespace.
    
6.  Enter the 'runtestcase' container in the ignite pod to execute the test case.

7.  Once the execution is completed, run make reset-migutbox to delete the mme and ignite pods.

8. make clean to cleanup the cluster as a whole.


**Helper commands:**

kubectl get pods -n omec 

kubectl describe pods mme-0 -n omec

kubectl logs mme-0 -n omec -c *container-name*

kubectl exec -it mme-0 -n omec  -c *mme-app* - /bin/bash

**Known Issue:**
The coreDNS service (kubectl get services -n kube-system) is assigned an ip address of x.x.x.3 
by the kubespray playbook. However the coreDNS ip in config is set as  x.x.x.10. This has to be 
changed to .3 in the below file once the playbook is completed:

sudo vi /var/lib/kubelet/config.yaml
sudo systemctl restart kubelet


