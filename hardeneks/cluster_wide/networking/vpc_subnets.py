import boto3
from kubernetes import client
import sys

from ...resources import Resources
from ...report import  print_console_message

def consider_public_and_private_mode(resources: Resources):
    status = True
    objectsList = None
    objectType = None
    message = None
    
    
    client = boto3.client("eks", region_name=resources.region)
    cluster_metadata = client.describe_cluster(name=resources.cluster)
    #pprint("cluster_metadata={}".format(cluster_metadata))
    endpoint_public_access  = cluster_metadata["cluster"]["resourcesVpcConfig"]["endpointPublicAccess"]
    endpoint_private_access = cluster_metadata["cluster"]["resourcesVpcConfig"]["endpointPrivateAccess"]

    if endpoint_public_access == True and endpoint_private_access == True:
        message = "EKS Cluster Endpoint is in Public and Private Mode"
    else:
        message = "EKS Cluster Endpoint is not in Public and Private Mode"
        status = False

    if endpoint_public_access:
        public_access_cidr_list  = cluster_metadata["cluster"]["resourcesVpcConfig"]["publicAccessCidrs"]
        if '0.0.0.0/0' in public_access_cidr_list :
            message = "EKS Cluster Endpoint is Public and Open to Internet Access ['0.0.0.0/0']"
            status = False
        else:
            message = "EKS Cluster Endpoint is Public and is not Open to Internet Access ['0.0.0.0/0']"
    
    return (status, message, objectsList, objectType)


