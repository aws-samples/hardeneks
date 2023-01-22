import boto3
from rich.console import Console
from rich.panel import Panel
from rich import print

from ...resources import Resources


console = Console()


def deploy_workers_onto_private_subnets(resources: Resources):
    
    status = None
    message = ""
    objectType = "PublicInstances"
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
        if instance["Instances"][0]["PublicDnsName"]:
            objectsList.append(instance)

    if objectsList:
        status = False
        message = "Place worker nodes on private subnets"
    else:
        status = True
        message = "worker nodes are on private subnets."
    
    return (status, message, objectsList, objectType)
    
    
def make_sure_inspector_is_enabled(resources: Resources):
    
    status = None
    message = ""
    objectType = None
    objectsList = []
    
    inspector2client = boto3.client("inspector2", region_name=resources.region)
    account_id = boto3.client(
        "sts", region_name=resources.region
    ).get_caller_identity()["Account"]

    response = inspector2client.batch_get_account_status(
        accountIds=[
            account_id,
        ]
    )

    resource_state = response["accounts"][0]["resourceState"]
    ec2_status = resource_state["ec2"]["status"]
    ecr_status = resource_state["ecr"]["status"]

    if ec2_status != "ENABLED" and ecr_status != "ENABLED":
        status = False
        message = "Enable Amazon Inspector for ec2 and ecr"
    else:
        status = True
        message = "Amazon Inspector is enabled for ec2 and ecr"

    return (status, message, objectsList, objectType)
    
    
    
 