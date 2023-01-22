from importlib import import_module

import sys
import boto3
from kubernetes import client
from rich import print

from rich.console import Console

from .report import print_console_message

from .report import colorMap

def cluster_data(resources, config, _type):

    current_eks_version = "1.24"
    eks_cluster_data = []
    
    eksclient = boto3.client("eks", region_name=resources.region)
    cluster_metadata = eksclient.describe_cluster(name=resources.cluster)
    cluster_version = cluster_metadata["cluster"]["version"]
    
    if cluster_version == current_eks_version:
        eks_cluster_data.append(  ["green", resources.cluster, cluster_version, "Cluster version is latest version"])
    else:
        eks_cluster_data.append(  ["yellow", resources.cluster, cluster_version, "Upgrade to latest version: {}".format(current_eks_version)])

    cluster_endpoint = cluster_metadata["cluster"]["endpoint"]
    eks_cluster_data.append(  ["green", "Cluster Endpoint URL", cluster_endpoint, ""])

    vpcId  = cluster_metadata["cluster"]["resourcesVpcConfig"]["vpcId"]
    subnetIds = cluster_metadata["cluster"]["resourcesVpcConfig"]["subnetIds"]
    
    
    eks_cluster_data.append(  ["green", "Cluster VPC Id", vpcId, ""])

    subnetIdsString = " ".join(subnetIds)
    eks_cluster_data.append(  ["green", "Cluster Subnets Id", subnetIdsString, ""])

    endpoint_public_access  = cluster_metadata["cluster"]["resourcesVpcConfig"]["endpointPublicAccess"]
    endpoint_private_access = cluster_metadata["cluster"]["resourcesVpcConfig"]["endpointPrivateAccess"]
    
    endpoibtAccessString = "public: " + str(endpoint_public_access) + ", " + "private: " + str(endpoint_private_access)
    eks_cluster_data.append(  ["green", "Cluster Emdpopint Access", endpoibtAccessString, ""])

    subnets = boto3.resource("ec2").subnets.filter(
        Filters=[{"Name": "vpc-id", "Values": [vpcId]}]
    )
    subnet_ids = [sn.id for sn in subnets]
    

    ec2client = boto3.client('ec2')
    subnetsList = ec2client.describe_subnets(SubnetIds=subnet_ids)
    
    totalAvailableIpAddressCount = 0
    for subnet in subnetsList['Subnets']:
        totalAvailableIpAddressCount += subnet['AvailableIpAddressCount']
        
    eks_cluster_data.append(  ["green", "Total Available IPs in the VPC", str(totalAvailableIpAddressCount), ""])    
        
    deployments = client.AppsV1Api().list_deployment_for_all_namespaces().items
    eks_cluster_data.append(  ["green", "Total No. of Deployments in Cluster", str(len(deployments)), ""])    
    
    services = client.CoreV1Api().list_service_for_all_namespaces().items
    eks_cluster_data.append(  ["green", "Total No. of Services in Cluster", str(len(services)), ""])    
    
    pods = client.CoreV1Api().list_pod_for_all_namespaces().items
    eks_cluster_data.append(  ["green", "Total No. of Pods in Cluster", str(len(pods)), ""])    
    
    
    nodeList = (client.CoreV1Api().list_node().items)
    eks_cluster_data.append(  ["green", "Total No. of Nodes in Cluster", str(len(nodeList)), ""])    

    eksmnglist = set()
    selfmnglist=set()
    
    for node in nodeList:
        labels = node.metadata.labels
        
        if 'eks.amazonaws.com/nodegroup' in labels.keys():
            
            eksmnglist.add(labels['eks.amazonaws.com/nodegroup'])
        elif 'alpha.eksctl.io/nodegroup-name' in labels.keys():
            
            selfmnglist.add(labels['alpha.eksctl.io/nodegroup-name'])
        elif 'karpenter.sh/provisioner-name' in labels.keys():          
            
            pass
        else:
            selfmnglist.add(node.metadata.name)
            
            
    if len(eksmnglist) >=1 :
        eks_cluster_data.append(  ["green", "List of EKS Managed node groups ib Cluster", ' '.join(eksmnglist), ""])
        
    if len(selfmnglist) >=1 :
        eks_cluster_data.append(  ["green", "List of Self Managed node groups ib Cluster", ' '.join(selfmnglist), ""])
        
                
    print_console_message(True, "aws-eks-best-practices", None, eks_cluster_data, "ClusterData")

    


def harden(resources, config, _type, pillarsList):
    
    console = Console()
    
    console.print()
    config = config[_type]
    
    eks_waf_report = {}
    
    for pillar in config.keys():

        if pillar in pillarsList:

            eks_waf_report[pillar] = []
            
            for section in config[pillar]:
                
                if resources.debug:
                    if _type == "cluster_wide":
                        console.rule(f"[b] Checking Rules for Scope: {_type} for Pillar: {pillar} Section: {section}", characters=" -")
                    else:
                        console.rule(f"[b] Checking Rules for Scope: {_type} for namespace: {resources.namespace} for Pillar: {pillar} Section: {section}", characters=" -")
                    
                console.print()
                
                for rule in config[pillar][section]:
                    module = import_module(f"hardeneks.{_type}.{pillar}.{section}")
                    try:
                        func = getattr(module, rule)
                    except AttributeError as exc:
                        print(f"Exception for rule={rule} : [bold][red]{exc}")
                    try:
                        (ret, message, objectsList, objectType) =func(resources)

                        if resources.debug:
                            print_console_message(ret, rule, message, objectsList, objectType)
                        
                        eks_waf_report[pillar].append(  {"rule": rule, "message": message, "ret": ret})
                        
                    except Exception as exc:
                        if _type == "cluster_wide":
                            print(f"Exception for rule {rule} in Section {section} for Pillar {pillar} for scope {_type}: [bold][red]{exc}")
                        else:
                            print(f"Exception for rule {rule} in Section {section} for Pillar {pillar} for scope {_type} for namespace: {resources.namespace}: [bold][red]{exc}")
            
            
            if _type == "cluster_wide":
                print_console_message(True, pillar, None, eks_waf_report, "Report")
            else:
                print_console_message(True, pillar, resources.namespace, eks_waf_report, "Report")
                
            eks_waf_report={}
            
            
        
