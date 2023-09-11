from ...resources import NamespacedResources
from hardeneks.rules import Rule, Result


class disallow_linux_capabilities(Rule):
    _type = "namespace_based"
    pillar = "security"
    section = "runtime_security"
    message = "Capabilities beyond the allowed list are disallowed."
    url = "https://aws.github.io/aws-eks-best-practices/security/docs/runtime/#consider-adddropping-linux-capabilities-before-writing-seccomp-policies"

    def check(self, namespaced_resources: NamespacedResources):
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
                if (
                    container.security_context
                    and container.security_context.capabilities
                    and container.security_context.capabilities.add
                ):
                    capabilities = set(
                        container.security_context.capabilities.add
                    )
                    if not capabilities.issubset(set(allowed_list)):
                        offenders.append(pod)

        self.result = Result(
            status=True, 
            resource_type="Pod",
            namespace=namespaced_resources.namespace,
            )
        if offenders:
            self.result = Result(
                status=False,
                resource_type="Pod",
                resources=[i.metadata.name for i in offenders],
                namespace=namespaced_resources.namespace,
            )
