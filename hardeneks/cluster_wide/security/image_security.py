import boto3

from ...report import print_repository_table
from ...resources import Resources


def use_immutable_tags_with_ecr(resources: Resources):
    offenders = []

    client = boto3.client("ecr")
    repositories = client.describe_repositories()
    for repository in repositories["repositories"]:
        if repository["imageTagMutability"] != "IMMUTABLE":
            offenders.append(repository)

    if offenders:
        print_repository_table(
            offenders,
            "imageTagMutability",
            "[red]Make image tags immutable.",
        )

    return offenders
