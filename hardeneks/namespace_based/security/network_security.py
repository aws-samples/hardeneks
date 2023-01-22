from rich.console import Console

from hardeneks.resources import NamespacedResources


console = Console()


def use_encryption_with_aws_load_balancers(namespaced_resources: NamespacedResources):
    
    status = None
    message = ""
    objectType = "Service"
    objectsList = []
    
    for service in namespaced_resources.services:
        annotations = service.metadata.annotations
        if annotations:
            ssl_cert = (
                "service.beta.kubernetes.io/aws-load-balancer-ssl-cert"
                in annotations
            )
            ssl_cert_port = annotations.get(
                "service.beta.kubernetes.io/aws-load-balancer-ssl-ports"
            )
            if not (ssl_cert and ssl_cert_port == "443"):
                objectsList.append(service)

    if objectsList:
        status = False
        message = "Make sure you specify an ssl cert"
    else:
        status = True
        message = "ssl cert are configured for the services"
    
    return (status, message, objectsList, objectType)




