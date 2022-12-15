import boto3
from kubernetes import client
from rich import print
from rich.panel import Panel
from rich.console import Console

from ...resources import Resources
from ...report import print_role_table, print_instance_metadata_table

console = Console()


def restrict_wildcard_for_cluster_roles(resources: Resources):
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
            "[red]ClusterRoles should not have '*' in Verbs or Resources",
            "[link=https://aws.github.io/aws-eks-best-practices/security/docs/iam/#employ-least-privileged-access-when-creating-rolebindings-and-clusterrolebindings]Click to see the guide[/link]",
            "ClusterRole",
        )
    return offenders


def check_endpoint_public_access(resources: Resources):
    client = boto3.client("eks", region_name=resources.region)
    cluster_metadata = client.describe_cluster(name=resources.cluster)
    endpoint_access = cluster_metadata["cluster"]["resourcesVpcConfig"][
        "endpointPublicAccess"
    ]
    if endpoint_access:
        print(
            Panel(
                "[red]EKS Cluster Endpoint is not Private",
                subtitle="[link=https://aws.github.io/aws-eks-best-practices/security/docs/iam/#make-the-eks-cluster-endpoint-private]Click to see the guide[/link]",
            )
        )
        console.print()
        return False

    return True


def check_aws_node_daemonset_service_account(resources: Resources):
    daemonset = client.AppsV1Api().read_namespaced_daemon_set(
        name="aws-node", namespace="kube-system"
    )

    if daemonset.spec.template.spec.service_account_name == "aws-node":
        print(
            Panel(
                "[red]Update the aws-node daemonset to use IRSA",
                subtitle="[link=https://aws.github.io/aws-eks-best-practices/security/docs/iam/#update-the-aws-node-daemonset-to-use-irsa]Click to see the guide[/link]",
            )
        )
        console.print()
        return False

    return True


def check_access_to_instance_profile(resources: Resources):
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
        print_instance_metadata_table(
            offenders,
            "[red]Restrict access to the instance profile assigned to nodes",
            "[link=https://aws.github.io/aws-eks-best-practices/security/docs/iam/#when-your-application-needs-access-to-imds-use-imdsv2-and-increase-the-hop-limit-on-ec2-instances-to-2]Click to see the guide[/link]",
        )
    return offenders


def disable_anonymous_access_for_cluster_roles(resources: Resources):
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
            "[red]Don't bind clusterroles to anonymous/unauthenticated groups",
            "[link=https://aws.github.io/aws-eks-best-practices/security/docs/iam/#review-and-revoke-unnecessary-anonymous-access]Click to see the guide[/link]",
            "ClusterRoleBinding",
        )

    return offenders
