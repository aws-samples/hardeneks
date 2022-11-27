from ...resources import NamespacedResources
from ...report import (
    print_pod_table,
)


def disallow_secrets_from_env_vars(resources: NamespacedResources):
    offenders = []

    for pod in resources.pods:
        for container in pod.spec.containers:
            if container.env:
                for env in container.env:
                    if env.value_from.secret_key_ref:
                        offenders.append(pod)
            if container.env_from:
                for env_from in container.env_from:
                    if env_from.secret_ref:
                        offenders.append(pod)

    if offenders:
        print_pod_table(offenders, "[red]Running as root is not allowed")

    return offenders
