import boto3
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


def ensure_cluster_autoscaler_and_cluster_versions_match(resources: Resources):

    eks_client = boto3.client("eks", region_name=resources.region)
    cluster_metadata = eks_client.describe_cluster(name=resources.cluster)

    cluster_version = cluster_metadata["cluster"]["version"]

    deployments = client.AppsV1Api().list_deployment_for_all_namespaces().items

    for deployment in deployments:
        if deployment.metadata.name == "cluster-autoscaler":
            ca_containers = deployment.spec.template.spec.containers
            ca_image = ca_containers[0].image
            ca_image_version = ca_image.split(":")[-1]
            if cluster_version not in ca_image_version:
                console.print(
                    Panel(
                        f"[red]CA({ca_image_version})-k8s({cluster_version}) Cross version compatibility is not recommended.",
                        subtitle="[link=https://aws.github.io/aws-eks-best-practices/cluster-autoscaling/#operating-the-cluster-autoscaler]Click to see the guide[/link]",
                    )
                )
                console.print()
                return False
            else:
                return True


def ensure_cluster_autoscaler_has_autodiscovery_mode(resources: Resources):

    deployments = client.AppsV1Api().list_deployment_for_all_namespaces().items

    for deployment in deployments:
        if deployment.metadata.name == "cluster-autoscaler":
            ca_containers = deployment.spec.template.spec.containers
            ca_command = ca_containers[0].command
            if not any(
                "node-group-auto-discover" in item for item in ca_command
            ):
                console.print(
                    Panel(
                        "[red]Auto discovery is not enabled for Cluster Autoscaler",
                        subtitle="[link=https://aws.github.io/aws-eks-best-practices/cluster-autoscaling/#operating-the-cluster-autoscaler]Click to see the guide[/link]",
                    )
                )
                console.print()
                return False
            else:
                break

    return True
