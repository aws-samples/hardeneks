from kubernetes import client
from rich import print
from rich.panel import Panel
from rich.console import Console

from ...resources import Resources


def check_metrics_server_is_running(resources: Resources):
    services = [
        i.metadata.name
        for i in client.CoreV1Api().list_service_for_all_namespaces().items
    ]

    console = Console()

    if "metrics-server" in services:
        return True
    else:
        print(
            Panel(
                "[red]Deploy metrics server.",
                subtitle="[link=https://aws.github.io/aws-eks-best-practices/reliability/docs/application/#run-kubernetes-metrics-server]Click to see the guide[/link]",
            )
        )
        console.print()
        return False


def check_vertical_pod_autoscaler_exists(resources: Resources):
    deployments = [
        i.metadata.name
        for i in client.AppsV1Api().list_deployment_for_all_namespaces().items
    ]

    console = Console()

    if "vpa-recommender" in deployments:
        return True
    else:
        print(
            Panel(
                "[red]Deploy vertical pod autoscaler if needed.",
                subtitle="[link=https://aws.github.io/aws-eks-best-practices/reliability/docs/application/#vertical-pod-autoscaler-vpa]Click to see the guide[/link]",
            )
        )
        console.print()
        return False
