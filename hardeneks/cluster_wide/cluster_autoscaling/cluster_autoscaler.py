from kubernetes import client
from rich.panel import Panel

from hardeneks import console
from ...resources import Resources


def check_any_cluster_autoscaler_exists(resources: Resources):

    deployments = [
        i.metadata.name
        for i in client.AppsV1Api().list_deployment_for_all_namespaces().items
    ]

    if not ("cluster-autoscaler" in deployments or "karpenter" in deployments):
        console.print(
            Panel(
                "[red]Cluster Autoscaler or Karpeneter is not deployed.",
                subtitle="[link=https://aws.github.io/aws-eks-best-practices/cluster-autoscaling/]Click to see the guide[/link]",
            )
        )
        console.print()
        return False
    else:
        return True
