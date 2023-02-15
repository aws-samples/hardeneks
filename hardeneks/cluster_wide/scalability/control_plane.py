import re
from rich.panel import Panel
import kubernetes

from hardeneks import console
from ...resources import Resources


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
