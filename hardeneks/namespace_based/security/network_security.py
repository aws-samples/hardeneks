from hardeneks.rules import Rule, Result
from hardeneks.resources import NamespacedResources


class use_encryption_with_aws_load_balancers(Rule):
    _type = "namespace_based"
    pillar = "security"
    section = "network_security"
    message = "Make sure you specify an ssl cert."
    url = "https://aws.github.io/aws-eks-best-practices/security/docs/network/#use-encryption-with-aws-load-balancers"

    def check(self, namespaced_resources: NamespacedResources):
        offenders = []
        for service in namespaced_resources.services:
            annotations = service.metadata.annotations
            if service.spec.type == 'LoadBalancer':
                if annotations:
                    ssl_cert = annotations.get("service.beta.kubernetes.io/aws-load-balancer-ssl-cert")
                    ssl_cert_port = annotations.get("service.beta.kubernetes.io/aws-load-balancer-ssl-ports")
                    if not (ssl_cert and ssl_cert_port):
                        offenders.append(service.metadata.name)
                else:
                    offenders.append(service.metadata.name)

        self.result = Result(
            status=True, 
            resource_type="Service",
            namespace=namespaced_resources.namespace,
            )
        if offenders:
            self.result = Result(
                status=False,
                resource_type="Service",
                resources=offenders,
                namespace=namespaced_resources.namespace,
            )


# TODO: Should add a check of ingresses for TLS enabled.