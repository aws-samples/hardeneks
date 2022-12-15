from rich.console import Console

from ...report import (
    print_service_table,
)
from hardeneks.resources import NamespacedResources


console = Console()


def use_encryption_with_aws_load_balancers(
    namespaced_resources: NamespacedResources,
):
    offenders = []
    for service in namespaced_resources.services:
        annotations = service.metadata.annotations
        if annotations:
            ssl_cert = (
                "service.beta.kubernetes.io/aws-load-balancer-ssl-cert"
                in annotations
            )
            ssl_cert_port = annotations.get(
                "service.beta.kubernetes.io/aws-load-balancer-ssl-ports"
            )
            if not (ssl_cert and ssl_cert_port == "443"):
                offenders.append(service)

    if offenders:
        print_service_table(
            offenders,
            "[red]Make sure you specify an ssl cert",
            "[link=https://aws.github.io/aws-eks-best-practices/security/docs/network/#use-encryption-with-aws-load-balancers]Click to see the guide[/link]",
        )
    return offenders
