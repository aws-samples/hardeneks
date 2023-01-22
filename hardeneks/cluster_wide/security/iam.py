import boto3
from kubernetes import client
from rich import print
from rich.panel import Panel
from rich.console import Console

from ...resources import Resources
from ...helper_functions import is_daemonset_exists_in_cluster

console = Console()


def disable_anonymous_access_for_cluster_roles(resources: Resources):
    
    status = None
    message = ""
    objectType = "ClusterRoleBinding"
    objectsList = []
    clusterrolenameslist = ""


    for cluster_role_binding in resources.cluster_role_bindings:
        if cluster_role_binding.subjects:
            for subject in cluster_role_binding.subjects:
                if (
                    subject.name == "system:unauthenticated"
                    or subject.name == "system:anonymous"
                ):
                    objectsList.append(cluster_role_binding.metadata.name)
                    #objectsList.append(cluster_role_binding)
                    clusterrolenameslist += cluster_role_binding.metadata.name

    
    #print("objectsList={}".format(objectsList))
    
    if objectsList:
        status = False
        message = "Clusterroles bound to to anonymous/unauthenticated groups: " + clusterrolenameslist
    else:
        status = True
        message = "There are no Clusterroles bound to to anonymous/unauthenticated groups"
    
    return (status, message, objectsList, objectType)

def check_endpoint_public_access(resources: Resources):

    status = None
    message = ""
    objectType = None
    objectsList = []

    
    client = boto3.client("eks", region_name=resources.region)
    cluster_metadata = client.describe_cluster(name=resources.cluster)
    endpoint_access = cluster_metadata["cluster"]["resourcesVpcConfig"][
        "endpointPublicAccess"
    ]
    
    if endpoint_access:
        status = False
        message = "EKS Cluster Endpoint is Public"
    else:
        status = True
        message = "EKS Cluster Endpoint is not Private"
        
    return (status, message, objectsList, objectType)
    


def check_aws_node_daemonset_service_account(resources: Resources):
    
    status = None
    message = ""
    objectType = None
    objectsList = []
    
    
    (doesDSExists, daemonset) = is_daemonset_exists_in_cluster("aws-node")
    
    if doesDSExists:

        if daemonset.spec.template.spec.service_account_name == "aws-node":
            status = False
            message = "Update the aws-node daemonset to use IRSA"
        else:
            status = True
            message = "aws-node daemonset uses IRSA"
    else:
        status = False
        message = "aws-node daemonset doesn't exist in the cluster"
        
    return (status, message, objectsList, objectType)


def check_access_to_instance_profile(resources: Resources):

    status = None
    message = ""
    objectType = "instanceMetadata"
    objectsList = []
    
    ec2client = boto3.client("ec2", region_name=resources.region)
    instance_metadata = ec2client.describe_instances(
        Filters=[
            {
                "Name": "tag:aws:eks:cluster-name",
                "Values": [
                    resources.cluster,
                ],
            },
        ]
    )

    for instance in instance_metadata["Reservations"]:
        if (
            instance["Instances"][0]["MetadataOptions"][
                "HttpPutResponseHopLimit"
            ]
            == 2
        ):
            objectsList.append(instance)
            status = False
            message = "access to the instance profile assigned to nodes is not restricted"
        else:
            status = True
            message = "access to the instance profile assigned to nodes is restricted"
    
    
    return (status, message, objectsList, objectType)


def restrict_wildcard_for_cluster_roles(resources: Resources):
    
    status = None
    message = ""
    objectType = "ClusterRole"
    objectsList = []
    clusterrolenameslist = ""
    
    for role in resources.cluster_roles:
        if role.rules:
            for rule in role.rules:
                if "*" in rule.verbs:
                    objectsList.append(role.metadata.name)
                if rule.resources and "*" in rule.resources:
                    objectsList.append(role.metadata.name)
                    clusterrolenameslist += role.metadata.name
                

    if objectsList:
        status = False
        message = "ClusterRoles with '*' in Verbs or Resources are: " + clusterrolenameslist
    else:
        status = True
        message = "There are no ClusterRoles with '*' in Verbs or Resources"
    
    return (status, message, objectsList, objectType)


