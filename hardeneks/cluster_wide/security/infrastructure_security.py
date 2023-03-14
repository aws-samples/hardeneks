import boto3

from ...resources import Resources
from hardeneks.rules import Rule, Result


class deploy_workers_onto_private_subnets(Result):
    _type = "cluster_wide"
    pillar = "security"
    section = "infrastructure_security"
    message = "Place worker nodes on private subnets."
    url = "https://aws.github.io/aws-eks-best-practices/security/docs/hosts/#deploy-workers-onto-private-subnets"

    def check(self, resources: Resources):
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
                offenders.append(instance["Instances"][0]["InstanceId"])

        self.result = Result(status=True, resource_type="Node")

        if offenders:
            self.result = Result(
                status=False, resource_type="Node", resources=offenders
            )


class make_sure_inspector_is_enabled(Rule):
    _type = "cluster_wide"
    pillar = "security"
    section = "infrastructure_security"
    message = "Enable Amazon Inspector for ec2 and ecr."
    url = "https://aws.github.io/aws-eks-best-practices/security/docs/hosts/#deploy-workers-onto-private-subnets"

    def check(self, resources: Resources):
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

        self.result = Result(
            status=True, resource_type="Inspector Configuration"
        )

        if ec2_status != "ENABLED" and ecr_status != "ENABLED":
            self.result = Result(
                status=False, resource_type="Inspector Configuration"
            )
