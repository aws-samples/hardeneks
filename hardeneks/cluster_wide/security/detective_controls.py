import boto3
from rich import print
from rich.panel import Panel
from rich.console import Console


from ...resources import Resources

console = Console()


def check_logs_are_enabled(resources: Resources):

    status = None
    message = ""
    objectType = None
    objectsList = []
    
    eksclient = boto3.client("eks", region_name=resources.region)
    cluster_metadata = eksclient.describe_cluster(name=resources.cluster)
    logs = cluster_metadata["cluster"]["logging"]["clusterLogging"][0][
        "enabled"
    ]
    if not logs:
        status = False
        message = "Enable control plane logs for auditing"
    else:
        status = True
        message = "Control plane logs are enabled for auditing"
        
    return (status, message, objectsList, objectType)
