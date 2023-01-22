from kubernetes import client
from rich import print
from rich.panel import Panel
from rich.console import Console

from ...resources import Resources


def check_metrics_server_is_running(resources: Resources):
    status = None
    message = ""
    objectType = None
    objectsList = []
    
    services = [
        i.metadata.name
        for i in client.CoreV1Api().list_service_for_all_namespaces().items
    ]

    if "metrics-server" in services:
        status =  True
        message = "Metrics server deployed"
    else:
        status =  False
        message = "Metrics server is not deployed"
    
    return (status, message, objectsList, objectType)

def check_vertical_pod_autoscaler_exists(resources: Resources):
    
    status = None
    message = ""
    objectType = None
    objectsList = []
    
    deployments = [
        i.metadata.name
        for i in client.AppsV1Api().list_deployment_for_all_namespaces().items
    ]

    if "vpa-recommender" in deployments:
        status =  True
        message = "Vertical pod autoscaler is deployed"
    else:
        status =  False
        message = "Deploy vertical pod autoscaler if needed"
        
    return (status, message, objectsList, objectType)


