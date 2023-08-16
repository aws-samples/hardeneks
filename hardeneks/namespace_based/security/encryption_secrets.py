from ...resources import NamespacedResources
from hardeneks.rules import Rule, Result


class disallow_secrets_from_env_vars(Rule):
    _type = "namespace_based"
    pillar = "security"
    section = "encryption_secrets"
    message = "Disallow secrets from env vars."
    url = "https://aws.github.io/aws-eks-best-practices/security/docs/data/#use-volume-mounts-instead-of-environment-variables"

    def check(self, namespaced_resources: NamespacedResources):
        offenders = []

        for pod in namespaced_resources.pods:
            for container in pod.spec.containers:
                if container.env:
                    for env in container.env:
                        if env.value_from and env.value_from.secret_key_ref:
                            offenders.append(pod)
                if container.env_from:
                    for env_from in container.env_from:
                        if env_from.secret_ref:
                            offenders.append(pod)

        self.result = Result(
            status=True, 
            resource_type="Pod",
            namespace=namespaced_resources.namespace
            )
        if offenders:
            self.result = Result(
                status=False,
                resource_type="Pod",
                resources=[i.metadata.name for i in offenders],
                namespace=namespaced_resources.namespace,
            )
