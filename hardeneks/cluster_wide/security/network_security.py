import boto3
from kubernetes import client
from rich.console import Console
from rich.panel import Panel
from rich import print


from ...resources import Resources
from ...report import print_namespace_table


console = Console()


def check_vpc_flow_logs(resources: Resources):
    client = boto3.client("eks", region_name=resources.region)
    cluster_metadata = client.describe_cluster(name=resources.cluster)

    vpc_id = cluster_metadata["cluster"]["resourcesVpcConfig"]["vpcId"]
    client = boto3.client("ec2", region_name=resources.region)

    flow_logs = client.describe_flow_logs(
        Filters=[{"Name": "resource-id", "Values": [vpc_id]}]
    )["FlowLogs"]

    if not flow_logs:
        print(
            Panel(
                "[red]Enable flow logs for your VPC.",
                subtitle="[link=https://aws.github.io/aws-eks-best-practices/security/docs/network/#log-network-traffic-metadata]Click to see the guide[/link]",
            )
        )
        console.print()
        return False


def check_awspca_exists(resources: Resources):
    services = client.CoreV1Api().list_service_for_all_namespaces().items
    for service in services:
        if service.metadata.name.startswith("aws-privateca-issuer"):
            return True

    print(
        Panel(
            "[red]Install aws privateca issuer for your certificates.",
            subtitle="[link=https://aws.github.io/aws-eks-best-practices/security/docs/network/#acm-private-ca-with-cert-manager]Click to see the guide[/link]",
        )
    )
    console.print()
    return False


def check_default_deny_policy_exists(resources: Resources):
    offenders = resources.namespaces

    for policy in resources.network_policies:
        offenders.remove(policy.metadata.namespace)

    if offenders:
        print_namespace_table(
            offenders,
            "[red]Namespaces that does not have default network deny policies",
            "[link=https://aws.github.io/aws-eks-best-practices/security/docs/network/#create-a-default-deny-policy]Click to see the guide[/link]",
        )

    return offenders
