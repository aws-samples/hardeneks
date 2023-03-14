import re
import kubernetes
from hardeneks import helpers
from hardeneks.rules import Rule, Result
from hardeneks import Resources


class check_EKS_version(Rule):
    _type = "cluster_wide"
    pillar = "scalability"
    section = "control_plane"
    message = "EKS Version Should be greater or equal to 1.24."
    url = "https://aws.github.io/aws-eks-best-practices/scalability/docs/control-plane/#use-eks-124-or-above"

    def check(self, resources: Resources):
        client = kubernetes.client.VersionApi()
        version = client.get_code()
        minor = version.minor

        if int(re.sub("[^0-9]", "", minor)) < 24:
            self.result = Result(
                status=False,
                resources=f"{version.major}.{minor}",
                resource_type="Cluster Version",
            )
        else:
            self.result = Result(status=True, resource_type="Cluster Version")


#
# check_kubectl_compression
# checks all clusters in config for disable-compression flag set to true
# if any cluster does not have setting, it returns False
class check_kubectl_compression(Rule):
    _type = "cluster_wide"
    pillar = "scalability"
    section = "control_plane"
    message = "`disable-compression` in kubeconfig should equal True"
    url = "https://aws.github.io/aws-eks-best-practices/scalability/docs/control-plane/#disable-kubectl-compression"

    def check(self, resources: Resources):
        kubeconfig = helpers.get_kube_config()
        for cluster in kubeconfig.get("clusters", []):
            clusterName = cluster.get("name", "")
            if resources.cluster in clusterName:
                if not (
                    cluster.get("cluster", {}).get(
                        "disable-compression", False
                    )
                ):
                    self.result = Result(
                        status=False, resource_type="Compression Setting"
                    )
                else:
                    self.result = Result(
                        status=True, resource_type="Compression Setting"
                    )
                break
