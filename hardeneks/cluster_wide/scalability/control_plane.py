import re
import kubernetes
import boto3
from hardeneks import helpers
from hardeneks.rules import Rule, Result
from hardeneks import Resources


class check_EKS_version(Rule):
    _type = "cluster_wide"
    pillar = "scalability"
    section = "control_plane"
    message = "Use an EKS version in standard support."
    url = "https://aws.github.io/aws-eks-best-practices/scalability/docs/control-plane/"

    def check(self, resources: Resources):
        eks_client = boto3.client("eks", region_name=resources.region)

        cluster_version = eks_client.describe_cluster(name=resources.cluster)["cluster"]["version"]
        # Get versions in standard support
        cluster_versions_response = eks_client.describe_cluster_versions()
        standard_support_versions = [
            v["clusterVersion"] 
            for v in cluster_versions_response.get("clusterVersions", [])
            if v.get("versionStatus") == "STANDARD_SUPPORT"
        ]

        self.result = Result(status=True, resource_type="Cluster Version")

        if cluster_version not in standard_support_versions:
            self.result = Result(
                status=False,
                resources=[cluster_version],
                resource_type="Cluster Version",
            )


#
# check_kubectl_compression
# checks all clusters in config for disable-compression flag set to true
# if any cluster does not have setting, it returns False
class check_kubectl_compression(Rule):
    _type = "cluster_wide"
    pillar = "scalability"
    section = "control_plane"
    message = "Enable `disable-compression` in kubeconfig."
    url = "https://aws.github.io/aws-eks-best-practices/scalability/docs/control-plane/#disable-kubectl-compression"

    def check(self, resources: Resources):
        kubeconfig = helpers.get_kube_config()
        for cluster in kubeconfig.get("clusters", []):
            clusterName = cluster.get("name", "")
            if resources.cluster in clusterName:
                if not (cluster.get("cluster", {}).get("disable-compression", False)):
                    self.result = Result(
                        status=False, 
                        resources=[resources.cluster],  
                        resource_type="Compression Setting"
                    )
                else:
                    self.result = Result(status=True, resource_type="Compression Setting")
                break
