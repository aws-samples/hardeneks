from rich.console import Console

from ...resources import Resources

from ...report import (
    print_namespace_table,
)

console = Console()


def ensure_namespace_quotas_exist(resources: Resources):

    offenders = resources.namespaces

    for quota in resources.resource_quotas:
        offenders.remove(quota.metadata.namespace)

    if offenders:
        print_namespace_table(
            offenders,
            "[red]Namespaces should have quotas assigned",
            "[link=https://aws.github.io/aws-eks-best-practices/security/docs/multitenancy/#namespaces]Click to see the guide[/link]",
        )

    return offenders
