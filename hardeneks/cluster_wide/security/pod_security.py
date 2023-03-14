import kubernetes

from ...resources import Resources
from hardeneks.rules import Rule, Result


class ensure_namespace_psa_exist(Rule):
    _type = "cluster_wide"
    pillar = "security"
    section = "pod_security"
    message = "Namespaces should have psa modes."
    url = "https://aws.github.io/aws-eks-best-practices/security/docs/pods/#pod-security-standards-pss-and-pod-security-admission-psa"

    def check(self, resources: Resources):
        offenders = []

        namespaces = kubernetes.client.CoreV1Api().list_namespace().items
        for namespace in namespaces:
            if namespace.metadata.name not in resources.namespaces:
                labels = namespace.metadata.labels.keys()
                if "pod-security.kubernetes.io/enforce" not in labels:
                    offenders.append(namespace.metadata.name)
                elif "pod-security.kubernetes.io/warn" not in labels:
                    offenders.append(namespace.metadata.name)
                elif not labels:
                    offenders.append(namespace.metadata.name)

        self.result = Result(status=True, resource_type="Namespace")
        if offenders:
            self.result = Result(
                status=False, resource_type="Namespace", resources=offenders
            )
