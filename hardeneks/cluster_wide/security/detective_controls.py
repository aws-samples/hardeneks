import boto3

from ...resources import Resources
from hardeneks.rules import Rule, Result


class check_logs_are_enabled(Rule):
    _type = "cluster_wide"
    pillar = "security"
    section = "detective_controls"
    message = "Enable control plane logs for auditing."
    url = "https://aws.github.io/aws-eks-best-practices/security/docs/detective/#enable-audit-logs"

    def check(self, resources: Resources):
        client = boto3.client("eks", region_name=resources.region)
        cluster_metadata = client.describe_cluster(name=resources.cluster)
        logs = cluster_metadata["cluster"]["logging"]["clusterLogging"][0][
            "enabled"
        ]
        self.result = Result(status=True, resource_type="Log Configuration")
        if not logs:
            self.result = Result(
                status=False, resource_type="Log Configuration"
            )
