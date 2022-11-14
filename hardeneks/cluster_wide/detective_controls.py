import boto3
from rich.console import Console


from ..resources import Resources

console = Console()


def check_logs_are_enabled(resources: Resources):
    client = boto3.client("eks", region_name=resources.region)
    cluster_metadata = client.describe_cluster(name=resources.cluster)
    logs = cluster_metadata["cluster"]["logging"]["clusterLogging"][0][
        "enabled"
    ]
    if not logs:
        console.print("Enable control plane logs for auditing", style="red")
        console.print()

    return logs
