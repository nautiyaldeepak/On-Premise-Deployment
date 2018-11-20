<h1 align="center">On Premise Deployment</h1>

## Description 
This project aims to solve on premise deployment problems. A cluster of microservices is created locally & then it is deployed on cloud. We have tried to solve the problem of remote incremental updates & remote debugging from this project. The cluster deployed can be monitored & regular health updates could be received. This project has also taken care of source code protection & disaster management.  

## Installation
- [Docker](https://docs.docker.com/docker-for-mac/install/)<br/>
- [Docker toobox](https://docs.docker.com/toolbox/toolbox_install_mac/)<br/>
- [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/)<br/>
- [minikube](https://github.com/kubernetes/minikube)<br/>
- [kops](https://github.com/kubernetes/kops)<br/>
- [Visual Studio Code](https://code.visualstudio.com/download)<br/>
- [AWS Command Line Interface](https://aws.amazon.com/cli/)<br/>
- [Jenkins](https://jenkins.io/download/)

## How to Use
Clone the repository & change the pwd
```console
$ git clone https://github.com/nautiyaldeepak/On-Premise-Deployment.git
$ cd On-Premise-Deployment/
```

Make sure that kubectl & minikube are running.
Check if kubectl is running
```console
$ kubectl version
$ minikube version
```

Now create a kubernetes deployment & expose the necessary ports. 
```console
$ kubectl create -f deployment.yaml
$ kubectl expose deployments jenkins-deployment pythonapp --type=NodePort
``` 

#### Configure Jenkins for remotely triggered incremental updates
1. Once the deployments & pods are up & running then we need to configure jenkins for incremental updates. Connect to jenkins from your web browser on port 8080. 
2. The jenkins startup screen will prompt up. There you will have to type in the administrator password. You can find jenkins password from jenkins-deployment logs. After that a plugin installation window will prompt up, here make sure to install the Git & GitHub plugin. 
3. Once plugins are installed, create an admin user & password. After that create a new job as freestyle project & then in the new job setup the configuration. Use Git as the source code management & type in the git [repository](https://github.com/nautiyaldeepak/On-Premise-Deployment.git). 
4. After that, set "GitHub hook trigger for GITScm polling" as build trigger. Now add "buildExecutable" script in shell exxcutable build. Jenkins is now configured.
5. Now we need to add a webhook to our GitHub repository. For that go to the [GitHub repo](https://github.com/nautiyaldeepak/On-Premise-Deployment.git), in settings add webhooks & set payload url as "http://jenkins-ip:8080/github-webhook/"

#### Setting up remote debugger using Visual Studio Code
1. To initialize remote debugger, you first need to [install ptvsd](https://github.com/Microsoft/ptvsd/) on your local computer. 
2. Now open the app.py file from vscode. Then open launch.json which is present in the github repo which you have cloned `.vscode/launch.json`. 
3. In launch.json change the host settings on line 12 to the IP address of the cluster running. 
4. Now in app.py first add a breakpoint on line 10 for testing purposes then select the debugger option and then click on the green start mark present on the top left side of the screen. The debugger will start and will hit the breakpoint.

#### Health alerts & Monitoring
In this project `cadvisor` is being used for monitoring purpose. Cadvisor is an independent container running which monitors other containers running in the system. `cadvisor` provides all the necessary metrices which needs to be monitored like CPU Utilization, Memory, Network Throughput & errors.
Unfortunately, `cadvisor` is only for monitoring and not for sending health alerts. 

I wanted to use sysdig which could have helped me both monitor & also get health alerts but it was a paid software. Sysdig shows the breakdown of information of containers in a much more dynamic way as compared to cadvisor. With Sysdig & Sysdig Inspect we can not just only monitor but also drill down each aspect of the container and also it helps us to troubleshoot the problems. It can generate health alerts on the basis of cpu utilization or on the basis of memory or on any error report and on many other parameters.

#### Source Code Protection
Source code can be protected by using one of the version control systems. In this project Git has been used for version control. For protecting the source code I could have kept the bucket private, but for demonstration purposes I have kept the bucket public. If I would have kept the bucket private then while configuring jenkins I will have to provide my Git credentials in source code management section so that jenkins can pull my repo. 

#### Disaster Management
For disaster management first comes the source code protection. We need to make sure that our source code is secure. For that we are using GitHub and it is also helping us to host are Git repository.
As far as the security of our containers is concerned, kubernetes takes care of that. Suppose we have launched 3 replicas in a single deployment, then we will have 3 pods running. If we forcefully remove all the pods or all three pods kubernetes will again spin up the necessary number of containers to keep the deployment running. Apart from that, if we are deploying our cluster on AWS ec2. EC2 has the availability of 99.99% and AWS also has its own infrastructure for disaster management according to AWS whitepapers. 

Docker also provides us with its own [Backup & Disaster Recovery](https://docs.docker.com/ee/ucp/admin/backups-and-disaster-recovery/) but it is only available for Docker EE. When we run the backup command docker creates an encrypted `backup.tar` file for us, which includes all running containers info & their dependencies.
```console
# Create a backup, encrypt it, and store it on /tmp/backup.tar
$ docker container run \
    --log-driver none --rm \
    --interactive \
    --name ucp \
    -v /var/run/docker.sock:/var/run/docker.sock \
    docker/ucp:3.1.0 backup \
    --id <ucp-instance-id> \
    --passphrase "secret" > /tmp/backup.tar

# Decrypt the backup and list its contents
$ gpg --decrypt /tmp/backup.tar | tar --list
```


Then we can save this `backup.tar` file in AWS S3 which has availability of 99.999999999% according to AWS whitepapers.
This backup can easily be restored using a backup specific docker run command. 
```console
$ docker container run --rm -i --name ucp \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v /tmp/backup.tar:/config/backup.tar \
    docker/ucp:3.1.0 restore -i
```

#### Setup kubernetes cluster on AWS
1. Use the aws configure to set AWS access key, Secret Key & default region.
2. Create an s3 bucket in any region of your choice (bucket name needs to be unique globally)
3. Enable versioning on the bucket created
4. Set two environment variables KOPS_CLUSTER_NAME and KOPS_STATE_STORE
5. Generate the cluster configuration

Use the following command to implement the above steps
```console
$ aws configure
$ aws s3api create-bucket --bucket python-app-deployment-bucket --region us-east-1
$ aws s3api put-bucket-versioning --bucket python-app-deployment-bucket --versioning-configuration Status=Enabled
$ export KOPS_CLUSTER_NAME=deployments.k8s.local
$ export KOPS_STATE_STORE=s3://python-app-deployment-bucket
$ kops create cluster --node-count=2 --node-size=t2.medium --zones=us-east-1a
```

To delete cluster
```console
$ kops delete cluster --name ${deployments.k8s.local} --yes
```

#### Local Deployment (For Testing)
For testing purposes you can also use `docker-compose.yml` template to quickly spin up the containers locally. The template will spin up 3 containers 1 for monitoring, 1 for jenkins & 1 `pythonapp` container. These containers have to be configured in the same manner, the only difference would be that rather than using cluster IP for remote debugging, we need to use localhost.

Follow the given commands for local containers deployment
```console
$ docker-compose up
```

Command to remove local container deployment
```console
$ docker-compose down
```

## Workflow
1. First we are creating a `pythonapp` docker container using Dockerfile. This dockerfile uses python3.6.5-slim as the base image. 
2. Jenkins and cadvisor are working independently. Cadvisor is monitoring all the running containers and providing all the details. Jenkins is being used with GitHub for incremental updates. 
3. Jenkins needs to be configured & it is dependent on Git repository. If the repo is public then there is no need to add credentials on source code management section, but if the repo is private credentials have to be added.
4. To configure AWS you will need `Access key ID` & `Secret Key ID`. You can create a user from IAM in AWS.
5. Cluster should only be deployed once you are finished with all the configuration.

## Reporting
You will be needing jenkins administrative password to configure jenkins. The administrative password can be found in jenkins container logs. At any time we can check how many containers are running by using `docker ps` command. To see the deployments use the command `kubectl get deployments`. To list all running pods use the command "kubectl get pods" & to list all running services use the command `kubectl get services`. 

## Performance & Scaling
In kubernetes cluster deployment we are using replicas. At any point in time we can change the number of replicas.
```console
$ kubectl scale --replicas=4 deployment/pythonapp
```
The above command will change the number of replicas in our pythonapp deployment

Kubernetes is responsible to make sure that all the pods are up & running. If one of the pods shuts down because of some error or otherwise, it will automatically spin up another pod with the same configuration to maintain the parity.

We are using `kops` to deploy our cluster on AWS cloud.
```console
$ kops create cluster --node-count=2 --node-size=t2.medium --zones=us-east-1a
```
The above cluster configuration will launch 2 ec2 instances. If we want to update the already existing cluster then we can use the following command
```console
$ kops update cluster --name ${KOPS_CLUSTER_NAME} --node-count=2 --yes
```
According to AWS whitepapers, the ec2 services will be available 99.99% of the time. So even if we loose one of our nodes, the cluster config will detect it & launch another node with required specs.

## Unresolved Issues
Jenkins is not working as expected for remote machines. Whenever we push a commit to GitHub, the webhook triggers jenkins but jenkins build fails for some reason.
On the local machine this jenkins setup is working well. Locally when the push is made to GitHub, build is triggered on Jenkins & it updates the code in the container.
