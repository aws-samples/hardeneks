import re
import kubernetes
from rich.panel import Panel
from hardeneks import helpers
from hardeneks import console
from hardeneks import Resources


def check_EKS_version(resources: Resources):
    client = kubernetes.client.VersionApi()
    version = client.get_code()
    minor = version.minor

    if int(re.sub("[^0-9]", "", minor)) < 24:
        console.print(
            Panel(
                f"[red]EKS Version Should be greater or equal too 1.24. Current Version == {version.major}.{version.minor}",
                subtitle="[link=https://aws.github.io/aws-eks-best-practices/scalability/docs/control-plane/#use-eks-124-or-above]Click to see the guide[/link]",
            )
        )
        console.print()
        return False

    return True

#
# check_kubectl_compression
# checks all clusters in config for disable-compression flag set to true
# if any cluster does not have setting, it returns False
def check_kubectl_compression(resources: Resources):
    kubeconfig = helpers.get_kube_config()
    isSetCorrectly = False
    for cluster in kubeconfig.get("clusters", []):
        clusterName = cluster.get("name", None)
        if (clusterName == resources.cluster):
            if cluster.get("cluster", {}).get("disable-compression", False) != True:
                console.print(
                    Panel(
                        f"[red]`disable-compression` in Cluster {clusterName}  should equal True",
                        subtitle="[link=https://aws.github.io/aws-eks-best-practices/scalability/docs/control-plane/#disable-kubectl-compression]Click to see the guide[/link]",
                    )
                )
                console.print()
            else:
                isSetCorrectly = True
            break
        
    
    return isSetCorrectly
