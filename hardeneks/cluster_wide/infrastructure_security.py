import boto3

from ..resources import Resources
from ..report import print_instance_public_table


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
        )
    return offenders
