import boto3
from kubernetes import client
from rich.console import Console
from rich.panel import Panel
from rich import print
import sys, copy


from ...resources import Resources

console = Console()


def check_vpc_flow_logs(resources: Resources):
    
    status = None
    message = ""
    objectType = "ClusterRole"
    objectsList = []
    clusterrolenameslist = ""
    
    eksclient = boto3.client("eks", region_name=resources.region)
    cluster_metadata = eksclient.describe_cluster(name=resources.cluster)

    vpc_id = cluster_metadata["cluster"]["resourcesVpcConfig"]["vpcId"]
    client = boto3.client("ec2", region_name=resources.region)

    flow_logs = client.describe_flow_logs(
        Filters=[{"Name": "resource-id", "Values": [vpc_id]}]
    )["FlowLogs"]

    if not flow_logs:
        status = False
        message = "Enable flow logs for your VPC"
    else:
        status = True
        message = "VPC flow logs are enabled"
            
    return (status, message, objectsList, objectType)


def check_awspca_exists(resources: Resources):
    
    status = False
    message = "Install aws privateca issuer for your certificates."
    objectType = None
    objectsList = []
    
    services = client.CoreV1Api().list_service_for_all_namespaces().items
    for service in services:
        if service.metadata.name.startswith("aws-privateca-issuer"):
            status = True
            message = "aws privateca issuer for certificates exists"

    return (status, message, objectsList, objectType)


def check_default_deny_policy_exists(resources: Resources):
    
    status = None
    message = ""
    objectType = "Namespace"
    objectsList = []
    
    objectsList = copy.deepcopy(resources.namespaces)
    
    for policy in resources.network_policies:
        if policy.metadata.namespace in objectsList:
            objectsList.remove(policy.metadata.namespace)
    
    if objectsList:
        status = False
        message = "Namespaces does not have default network deny policies"
    else:
        status = True
        message = "Namespaces have default network deny policies"
    
    return (status, message, objectsList, objectType)
