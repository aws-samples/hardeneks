import kubernetes

from ...resources import Resources

from ...report import (
    print_namespace_table,
)


def ensure_namespace_psa_exist(resources: Resources):
    offenders = []
    namespaces = kubernetes.client.CoreV1Api().list_namespace().items
    for namespace in namespaces:
        if namespace.metadata.name not in resources.namespaces:
            labels = namespace.metadata.labels.keys()
            if "pod-security.kubernetes.io/enforce" not in labels:
                offenders.append(namespace.metadata.name)
            elif "pod-security.kubernetes.io/warn" not in labels:
                offenders.append(namespace.metadata.name)

    if offenders:
        print_namespace_table(
            offenders,
            "[red]Namespaces should have psa modes.",
            "[link=https://aws.github.io/aws-eks-best-practices/security/docs/pods/#pod-security-standards-pss-and-pod-security-admission-psa]Click to see the guide[/link]",
        )

    return offenders
