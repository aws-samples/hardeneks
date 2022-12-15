import boto3

from ...report import print_repository_table
from ...resources import Resources


def use_immutable_tags_with_ecr(resources: Resources):
    offenders = []

    client = boto3.client("ecr", region_name=resources.region)
    repositories = client.describe_repositories()
    for repository in repositories["repositories"]:
        if repository["imageTagMutability"] != "IMMUTABLE":
            offenders.append(repository)

    if offenders:
        print_repository_table(
            offenders,
            "imageTagMutability",
            "[red]Make image tags immutable.",
            "[link=https://aws.github.io/aws-eks-best-practices/security/docs/image/#use-immutable-tags-with-ecr]Click to see the guide[/link]",
        )

    return offenders
