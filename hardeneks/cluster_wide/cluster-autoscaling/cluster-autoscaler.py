import boto3
from kubernetes import client
from rich import print

import sys

from ...resources import Resources
from ...report import   print_console_message
from ...helper_functions import is_deployment_exists_in_namespace

def check_any_cluster_autoscaler_exists(resources: Resources):
    
    status = True
    objectsList = None
    objectType = None
    message = ""
    
    docs_link = "https://aws.github.io/aws-eks-best-practices/cluster-autoscaling/"
    deployments = [
        i.metadata.name
        for i in client.AppsV1Api().list_deployment_for_all_namespaces().items
    ]
    
    #pprint("deployments={}".format(deployments))

    if "cluster-autoscaler" in deployments:
        message = "Kubernetes Cluster Autoscaler is deployed"
    elif "karpenter" in deployments:
        message = "Karpeneter is deployed"
    else:
        message = "Kubernetes Cluster Autoscaler or Karpeneter is not deployed"
        status = False
    
    return (status, message, objectsList, objectType)
    
def ensure_cluster_autoscaler_and_cluster_versions_match(resources: Resources):
    
    status = True
    objectsList = None
    objectType = None
    message = ""
    
    eksclient = boto3.client("eks", region_name=resources.region)
    cluster_metadata = eksclient.describe_cluster(name=resources.cluster)
    
    cluster_version = cluster_metadata["cluster"]["version"]
    
    #print("cluster_version={}".format(cluster_version))
    
    deployments = (client.AppsV1Api().list_namespaced_deployment("kube-system").items)
        
    #print("deployments={}".format(deployments))    
    
    ca_version = None
    ca_containers = None
    
    for deployment in deployments:
        if deployment.metadata.name == "cluster-autoscaler":
            ca_containers = deployment.spec.template.spec.containers
            ca_image = ca_containers[0].image
            ca_image_version = ca_image.split(':')[-1]
            #print("ca_image={} ca_image_version={}".format(ca_image, ca_image_version))
            
            versions = "Kubernetes Cluster Autoscaler Version (" + ca_image_version + ") and Cluster Version (" + cluster_version + ")"
            
            if cluster_version in ca_image_version:
                message = versions + " match"
            else:
                message = versions + " do not match"
                status = False

    if message == "":
        message = "Kubernetes Cluster Autoscaler is not deployed in the cluster"
        status = False
        
    return (status, message, objectsList, objectType)
    
    
def ensure_cluster_autoscaler_has_autodiscovery_mode(resources: Resources):
    
    status = True
    objectsList = None
    objectType = None
    message = ""
    
    deployments = (client.AppsV1Api().list_namespaced_deployment("kube-system").items)
    
    for deployment in deployments:
        if deployment.metadata.name == "cluster-autoscaler":
            ca_containers = deployment.spec.template.spec.containers
            ca_command = ca_containers[0].command
            for item in ca_command:
                if 'node-group-auto-discovery' in item:
                    message = "Kubernetes Cluster Autoscaler is configured with Auto Discovery Mode"
                    break
                    #print("item={}".format(item))
                    
    if message == "":
        message = "Kubernetes Cluster Autoscaler is not deployed in the cluster"
        status = False

    return (status, message, objectsList, objectType)
    
    
                
def ensure_cluster_autoscaler_has_three_replicas(resources: Resources):
    
    status = True
    objectsList = None
    objectType = None
    message = ""

    deployments = (client.AppsV1Api().list_namespaced_deployment("kube-system").items)
    
    for deployment in deployments:
        if deployment.metadata.name == "cluster-autoscaler":
            ca_replicas = deployment.spec.replicas
            if ca_replicas >= 3:
                message = "Kubernetes Cluster Autoscaler has {} replicas".format(ca_replicas)
            else:
                message = "Kubernetes Cluster Autoscaler has only {} replicas".format(ca_replicas)
                status = False
            break
        
    if message == "":
        message = "Kubernetes Cluster Autoscaler is not deployed in the cluster"
        status = False
        
    return (status, message, objectsList, objectType)

def use_separate_iam_role_for_cluster_autoscaler(resources: Resources):

    status = True
    objectsList = None
    objectType = None
    message = ""
    
    (ret, deploymentData) = is_deployment_exists_in_namespace("cluster-autoscaler", "kube-system")
    if ret:
        sa = deploymentData.spec.template.spec.service_account_name
        sa_data = client.CoreV1Api().read_namespaced_service_account(sa, 'kube-system', pretty="true")
        #print(sa_data.metadata.annotations.keys())
        
        if 'eks.amazonaws.com/role-arn' in sa_data.metadata.annotations.keys():
            message = "cluster-autoscaler deployment uses a dedicated IAM Role (IRSA)"
        else:
            message = "cluster-autoscaler deployment does not use a dedicated IAM Role (IRSA)"
            status = False
    else:
        message = "Kubernetes Cluster Autoscaler is not deployed in the cluster"
        status = False
        
    return (status, message, objectsList, objectType)
    
    
def employ_least_privileged_access_to_the_IAM_role(resources: Resources):

    status = True
    objectsList = None
    objectType = None
    message = ""
    
    iam_client = boto3.client('iam')
    
    
    (ret, deploymentData) = is_deployment_exists_in_namespace("cluster-autoscaler", "kube-system")
    if ret:

        sa = deploymentData.spec.template.spec.service_account_name
        sa_data = client.CoreV1Api().read_namespaced_service_account(sa, 'kube-system', pretty="true")
        #print(sa_data.metadata.annotations.keys())
        
        if 'eks.amazonaws.com/role-arn' in sa_data.metadata.annotations.keys():
            sa_iam_role_arn = sa_data.metadata.annotations['eks.amazonaws.com/role-arn']
            #print("sa_iam_role_arn={}".format(sa_iam_role_arn))
            #response = iam_client.list_role_policies(RoleName=sa_iam_role)
            sa_iam_role = sa_iam_role_arn.split('/')[-1]
            #print("sa_iam_role={}".format(sa_iam_role))
            policyList = iam_client.list_attached_role_policies(RoleName=sa_iam_role)
            #print("policyList={}".format(policyList))
            
            administratorAccess = None
            leastPrivelegedAccess =  None
            listofActions = []
            for policy in policyList['AttachedPolicies']:
                
                if policy['PolicyArn'] == 'arn:aws:iam::aws:policy/AdministratorAccess':
                    administratorAccess = True
                
                #print("PolicyName={} PolicyArn={}".format(policy['PolicyName'], policy['PolicyArn']))
                policyData = iam_client.get_policy(PolicyArn=policy['PolicyArn'])
                #print("policyData={}".format(policyData))
                policyDefaultVersion = policyData['Policy']['DefaultVersionId']
                #print("policyDefaultVersion={}".format(policyDefaultVersion))
                
                policyDocument = iam_client.get_policy_version(PolicyArn=policy['PolicyArn'], VersionId=policyDefaultVersion)
                
                policyStatements = policyDocument['PolicyVersion']['Document']['Statement']
                #print("policyDocument={}".format(policyStatements))
                
                for statement in policyStatements:
                    listofActions.extend(statement['Action'])
                
                #print("listofActions={}".format(listofActions))
                
            if 'autoscaling:SetDesiredCapacity' in listofActions and 'autoscaling:TerminateInstanceInAutoScalingGroup' in listofActions:
                leastPrivelegedAccess = True
    
            if administratorAccess is None and  leastPrivelegedAccess:
                message = "cluster-autoscaler has least privileged access to the IAM role"
            else:
                message = "cluster-autoscaler does not have least privileged access to the IAM role"
                status = False
        else:
            message = "cluster-autoscaler deployment does not use a dedicated IAM Role (IRSA)"
            status = False
    else:
        message = "Kubernetes Cluster Autoscaler is not deployed in the cluster"
        status = False

    return (status, message, objectsList, objectType)    

def use_managed_nodegroups(resources: Resources):
    
    status = True
    objectsList = None
    objectType = None
    message = ""
    
    eksclient = boto3.client("eks", region_name=resources.region)
    cluster_metadata = eksclient.describe_cluster(name=resources.cluster)
    
    cluster_version = cluster_metadata["cluster"]["version"]
    
    #print("cluster_version={}".format(cluster_version))
    
    eksmnglist = set()
    selfmnglist=set()
    
    nodeList = (client.CoreV1Api().list_node().items)
    for node in nodeList:
        labels = node.metadata.labels
        #print("nodeName={} nodegroup={}".format(node.metadata.name, labels ))
        if 'eks.amazonaws.com/nodegroup' in labels.keys():
            #print("nodeName={} managed nodegroup={}".format(node.metadata.name, labels['eks.amazonaws.com/nodegroup'] ))
            eksmnglist.add(labels['eks.amazonaws.com/nodegroup'])
        elif 'alpha.eksctl.io/nodegroup-name' in labels.keys():
            #print("nodeName={} self managed nodegroup={}".format(node.metadata.name, labels['alpha.eksctl.io/nodegroup-name'] ))
            selfmnglist.add(labels['alpha.eksctl.io/nodegroup-name'])
        elif 'karpenter.sh/provisioner-name' in labels.keys():          
            #print("nodeName={} Karpeneter managed provisioner={}".format(node.metadata.name, labels['karpenter.sh/provisioner-name'] ))
            pass
        else:
            selfmnglist.add(node.metadata.name)
            #print("nodeName={} self managed with node labels={}".format(node.metadata.name, labels ))
            
    #print("eksmnglist={} selfmnglist={}".format(eksmnglist, selfmnglist))
    
    if len(selfmnglist) == 0:
        message = "cluster has only managed node groups :{}".format(eksmnglist)
    else:
        message = "cluster has self managed node groups :{}".format(selfmnglist)
        status = False
        #print("keys={}".format(labels.keys()))
        #print("nodes={}".format(node.metadata.labels))
        #print("nodes={}".format(node['metadata']['labels']))

                    
    return (status, message, objectsList, objectType)


def ensure_uniform_instance_types_in_nodegroups(resources: Resources):

    status = True
    objectsList = None
    objectType = None
    message = ""
    
        
    func_name = sys._getframe().f_code.co_name
    docs_link = "https://aws.github.io/aws-eks-best-practices/cluster-autoscaling/"
    
    eksclient = boto3.client("eks", region_name=resources.region)
    cluster_metadata = eksclient.describe_cluster(name=resources.cluster)
    
    cluster_version = cluster_metadata["cluster"]["version"]
    
    #print("cluster_version={}".format(cluster_version))

    nodegroupList = {}
    nodegroupInstanceSizesList={}
    
    nodeList = (client.CoreV1Api().list_node().items)
    for node in nodeList:
        labels = node.metadata.labels
        #print("nodeName={} nodegroup={}".format(node.metadata.name, labels ))
        if 'eks.amazonaws.com/nodegroup' in labels.keys():
            #print("nodeName={} managed nodegroup={}".format(node.metadata.name, labels['eks.amazonaws.com/nodegroup'] ))
            nodegroupName = labels['eks.amazonaws.com/nodegroup']
            if nodegroupName not in nodegroupList.keys():
                nodegroupList[nodegroupName] = []
            nodegroupList[nodegroupName].append(labels['beta.kubernetes.io/instance-type'])
            #eksmnglist.add(labels['eks.amazonaws.com/nodegroup'])
        elif 'alpha.eksctl.io/nodegroup-name' in labels.keys():
            nodegroupName = labels['alpha.eksctl.io/nodegroup-name']
            if nodegroupName not in nodegroupList.keys():
                nodegroupList[nodegroupName] = []
            nodegroupList[nodegroupName].append(labels['beta.kubernetes.io/instance-type'])            
            #print("nodeName={} self managed nodegroup={}".format(node.metadata.name, labels['alpha.eksctl.io/nodegroup-name'] ))
            #selfmnglist.add(labels['alpha.eksctl.io/nodegroup-name'])
        elif 'karpenter.sh/provisioner-name' in labels.keys():          
            #print("nodeName={} Karpeneter managed provisioner={}".format(node.metadata.name, labels['karpenter.sh/provisioner-name'] ))
            pass
        else:
            pass
            
            #print("nodeName={} self managed with node labels={}".format(node.metadata.name, labels ))
            
    
    #nodegroupList['ng-3f4edeea'].append('m5.xlarge')
    #nodegroupList['mng2'].append('m5.2xlarge')
    #print("nodegroupList={}".format(nodegroupList))
    
    descriptionMessage = "These nodegroups contain non uniform instance types :"
    
    ec2client = boto3.client('ec2')
    isNonUniformNodegroupsExists = None
    for nodegroupName, instanceTypesList in nodegroupList.items():
        instanceTypesData = ec2client.describe_instance_types(InstanceTypes=instanceTypesList)
        #print("instanceTypesData={}".format(instanceTypesData))
        nodegroupInstanceSizesList[nodegroupName] = set()      
        for instanceData in instanceTypesData['InstanceTypes']:
            #print("InstanceType={} DefaultVCpus={} SizeInMiB={}".format(instanceData['InstanceType'], instanceData['VCpuInfo']['DefaultVCpus'], instanceData['MemoryInfo']['SizeInMiB']))
            DefaultVCpus=instanceData['VCpuInfo']['DefaultVCpus']
            SizeInMiB=instanceData['MemoryInfo']['SizeInMiB']
            nodegroupInstanceSizesList[nodegroupName].add((DefaultVCpus, int(SizeInMiB/1024)))
        
        if len(nodegroupInstanceSizesList[nodegroupName]) > 1:
            descriptionMessage += " " + nodegroupName
            isNonUniformNodegroupsExists = True
            
    #print("nodegroupInstanceSizesList={}".format(nodegroupInstanceSizesList))
    #print("descriptionMessage={}".format(descriptionMessage))

    
    if not isNonUniformNodegroupsExists:
        message = "cluster has only unfirm instance types in the node groups"
    else:
        message = descriptionMessage
        status =  False
        #print("keys={}".format(labels.keys()))
        #print("nodes={}".format(node.metadata.labels))
        #print("nodes={}".format(node['metadata']['labels']))
                    
    return (status, message, objectsList, objectType)
                        