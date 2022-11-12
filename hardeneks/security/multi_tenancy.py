from rich.console import Console

from ..resources import NamespacedResources

from ..report import (
    print_namespace_table,
)

console = Console()


def ensure_namespace_quotas_exist(namespaced_resources: NamespacedResources):

    offenders = [i.metadata.name for i in namespaced_resources.namespaces]

    for quota in namespaced_resources.resource_quotas:
        offenders.remove(quota.metadata.namespace)

    if offenders:
        print_namespace_table(
            offenders,
            "Namespaces should have quotas assigned",
        )

    return offenders
