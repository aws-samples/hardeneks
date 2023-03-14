import boto3

from ...resources import Resources
from hardeneks.rules import Rule, Result


class use_immutable_tags_with_ecr(Rule):
    _type = "cluster_wide"
    pillar = "security"
    section = "image_security"
    message = "Make image tags immutable."
    url = "https://aws.github.io/aws-eks-best-practices/security/docs/image/#use-immutable-tags-with-ecr"

    def check(self, resources: Resources):
        offenders = []

        client = boto3.client("ecr", region_name=resources.region)
        repositories = client.describe_repositories()
        for repository in repositories["repositories"]:
            if repository["imageTagMutability"] != "IMMUTABLE":
                offenders.append(repository)

        self.result = Result(status=True, resource_type="ECR Repository")
        if offenders:
            self.result = Result(
                status=False,
                resource_type="ECR Repository",
                resources=[i["repositoryName"] for i in offenders],
            )
