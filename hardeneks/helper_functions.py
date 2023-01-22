import boto3
from kubernetes import client

def is_deployment_exists_in_namespace(deploymentName, namespace):
    
    deployments = (client.AppsV1Api().list_namespaced_deployment(namespace).items)
    
    for deployment in deployments:
        if deployment.metadata.name == deploymentName:
            return (True, deployment)
    
    return (False, None)
    

def is_daemonset_exists_in_cluster(dsName):
    
    dsList = (client.AppsV1Api().list_daemon_set_for_all_namespaces().items)
    
    for ds in dsList:
        if ds.metadata.name == dsName:
            return (True, ds)
    
    return (False, None)    
