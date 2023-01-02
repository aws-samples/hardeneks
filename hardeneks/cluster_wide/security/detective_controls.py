import boto3
from rich.panel import Panel

from hardeneks import console
from ...resources import Resources


def check_logs_are_enabled(resources: Resources):
    client = boto3.client("eks", region_name=resources.region)
    cluster_metadata = client.describe_cluster(name=resources.cluster)
    logs = cluster_metadata["cluster"]["logging"]["clusterLogging"][0][
        "enabled"
    ]
    if not logs:
        console.print(
            Panel(
                "[red]Enable control plane logs for auditing",
                subtitle="[link=https://aws.github.io/aws-eks-best-practices/security/docs/detective/#enable-audit-logs]Click to see the guide[/link]",
            )
        )
        console.print()

    return logs
