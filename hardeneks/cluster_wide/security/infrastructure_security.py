import boto3
from rich.console import Console
from rich.panel import Panel
from rich import print

from ...resources import Resources
from ...report import print_instance_public_table


console = Console()


def deploy_workers_onto_private_subnets(resources: Resources):
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
        if instance["Instances"][0]["PublicDnsName"]:
            offenders.append(instance)

    if offenders:
        print_instance_public_table(
            offenders,
            "[red]Place worker nodes on private subnets.",
            "[link=https://aws.github.io/aws-eks-best-practices/security/docs/hosts/#deploy-workers-onto-private-subnets]Click to see the guide[/link]",
        )
    return offenders


def make_sure_inspector_is_enabled(resources: Resources):
    client = boto3.client("inspector2", region_name=resources.region)
    account_id = boto3.client(
        "sts", region_name=resources.region
    ).get_caller_identity()["Account"]

    response = client.batch_get_account_status(
        accountIds=[
            account_id,
        ]
    )

    resource_state = response["accounts"][0]["resourceState"]
    ec2_status = resource_state["ec2"]["status"]
    ecr_status = resource_state["ecr"]["status"]

    if ec2_status != "ENABLED" and ecr_status != "ENABLED":
        print(
            Panel(
                "[red]Enable Amazon Inspector for ec2 and ecr",
                subtitle="[link=https://aws.github.io/aws-eks-best-practices/security/docs/hosts/#run-amazon-inspector-to-assess-hosts-for-exposure-vulnerabilities-and-deviations-from-best-practices]Click to see the guide[/link]",
            )
        )
        console.print()
        return False

    return True
