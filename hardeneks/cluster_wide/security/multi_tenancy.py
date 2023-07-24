from ...resources import Resources
from hardeneks.rules import Rule, Result


class ensure_namespace_quotas_exist(Rule):
    _type = "cluster_wide"
    pillar = "security"
    section = "multi_tenancy"
    message = "Namespaces should have quotas assigned."
    url = "https://aws.github.io/aws-eks-best-practices/security/docs/multitenancy/#namespaces"

    def check(self, resources: Resources):
        offenders = resources.namespaces

        for quota in resources.resource_quotas:
            offenders.remove(quota.metadata.namespace)

        self.result = Result(status=True, resource_type="Namespace")
        if offenders:
            self.result = Result(
                status=False, resources=offenders, resource_type="Namespace"
            )
