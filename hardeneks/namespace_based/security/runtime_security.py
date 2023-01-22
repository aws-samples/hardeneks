from rich import print

from ...resources import NamespacedResources


def disallow_linux_capabilities(namespaced_resources: NamespacedResources):
    
    status = None
    message = ""
    objectType = "Pod"
    objectsList = []
    
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
            if (
                container.security_context
                and container.security_context.capabilities
            ):
                if container.security_context.capabilities.add:
                    capabilities = set(container.security_context.capabilities.add)
                    if not capabilities.issubset(set(allowed_list)):
                        objectsList.append(pod)

    if objectsList:
        status = False
        message = "Capabilities beyond the allowed list are allowed"
    else:
        status = True
        message = "Capabilities beyond the allowed list are disallowed"
    
    return (status, message, objectsList, objectType)



