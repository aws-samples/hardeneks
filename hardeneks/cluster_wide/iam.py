import boto3
from kubernetes import client
from rich.console import Console

from ..resources import NamespacedResources
from ..report import print_role_table, print_instance_table

console = Console()


def restrict_wildcard_for_cluster_roles(resources: NamespacedResources):
    offenders = []

    for role in resources.cluster_roles:
        for rule in role.rules:
            if "*" in rule.verbs:
                offenders.append(role)
            if rule.resources and "*" in rule.resources:
                offenders.append(role)

    if offenders:
        print_role_table(
            offenders,
            "ClusterRoles should not have '*' in Verbs or Resources",
            "ClusterRole",
        )
    return offenders


def check_endpoint_public_access(resources: NamespacedResources):
    client = boto3.client("eks", region_name=resources.region)
    cluster_metadata = client.describe_cluster(name=resources.cluster)
    endpoint_access = cluster_metadata["cluster"]["resourcesVpcConfig"][
        "endpointPublicAccess"
    ]
    if endpoint_access:
        console.print("EKS Cluster Endpoint is not Private", style="red")
        console.print()
        return False

    return True


def check_aws_node_daemonset_service_account(resources: NamespacedResources):
    daemonset = client.AppsV1Api().read_namespaced_daemon_set(
        name="aws-node", namespace="kube-system"
    )

    if daemonset.spec.template.spec.service_account_name == "aws-node":
        console.print("Update the aws-node daemonset to use IRSA", style="red")
        console.print()
        return False

    return True


def check_access_to_instance_profile(resources: NamespacedResources):
    client = boto3.client("ec2", region_name=resources.region)
    offenders = []

    instance_metadata = client.describe_instances(
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
        if (
            instance["Instances"][0]["MetadataOptions"][
                "HttpPutResponseHopLimit"
            ]
            == 2
        ):
            offenders.append(instance)

    if offenders:
        print_instance_table(
            offenders,
            "Restrict access to the instance profile assigned to nodes",
        )
    return offenders


def disable_anonymous_access_for_cluster_roles(resources: NamespacedResources):
    offenders = []

    for cluster_role_binding in resources.cluster_role_bindings:
        if cluster_role_binding.subjects:
            for subject in cluster_role_binding.subjects:
                if (
                    subject.name == "system:unauthenticated"
                    or subject.name == "system:anonymous"
                ):
                    offenders.append(cluster_role_binding)

    if offenders:
        print_role_table(
            offenders,
            "Don't bind clusterroles to anonymous or unauthenticated groups",
            "ClusterRoleBinding",
        )

    return offenders
