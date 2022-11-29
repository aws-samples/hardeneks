from rich import print

from ...resources import NamespacedResources
from ...report import print_pod_table


def disallow_linux_capabilities(namespaced_resources: NamespacedResources):
    offenders = []

    allowed_list = [
        "AUDIT_WRITE",
        "CHOWN",
        "DAC_OVERRIDE",
        "FOWNER",
        "FSETID",
        "KILL",
        "MKNOD",
        "NET_BIND_SERVICE",
        "SETFCAP",
        "SETGID",
        "SETPCAP",
        "SETUID",
        "SYS_CHROOT",
    ]
    for pod in namespaced_resources.pods:
        for container in pod.spec.containers:
            if container.security_context.capabilities:
                capabilities = set(container.security_context.capabilities.add)
                if not capabilities.issubset(set(allowed_list)):
                    offenders.append(pod)

    if offenders:
        print()
        print(allowed_list)
        print_pod_table(
            offenders,
            """
            [red]Capabilities beyond the allowed list are disallowed.
            """,
        )

    return offenders
