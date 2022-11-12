import boto3
from rich.console import Console


from ..resources import NamespacedResources

console = Console()


def check_logs_are_enabled(namespaced_resources: NamespacedResources):
    client = boto3.client("eks", region_name=namespaced_resources.region)
    cluster_metadata = client.describe_cluster(
        name=namespaced_resources.cluster
    )
    logs = cluster_metadata["cluster"]["logging"]["clusterLogging"][0][
        "enabled"
    ]
    if not logs:
        console.print("Enable control plane logs for auditing", style="red")
        console.print()

    return logs
