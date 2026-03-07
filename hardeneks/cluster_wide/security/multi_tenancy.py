from ...resources import Resources
from hardeneks.rules import Rule, Result


class ensure_namespace_quotas_exist(Rule):
    _type = "cluster_wide"
    pillar = "security"
    section = "multi_tenancy"
    message = "Namespaces should have quotas assigned."
    url = "https://aws.github.io/aws-eks-best-practices/security/docs/multitenancy/#namespaces"

    def check(self, resources: Resources):
        offenders = set(resources.namespaces)
        
        for quota in resources.resource_quotas:
            offenders.discard(quota.metadata.namespace)

        self.result = Result(status=True, resource_type="Namespace")
        if offenders:
            self.result = Result(
                status=False, resources=list(offenders), resource_type="Namespace"
            )
