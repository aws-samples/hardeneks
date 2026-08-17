from hardeneks.rules import Rule, Result
from hardeneks.resources import Resources


class check_metrics_server_is_running(Rule):
    _type = "cluster_wide"
    pillar = "reliability"
    section = "applications"
    message = "Deploy Metrics Server."
    url = "https://aws.github.io/aws-eks-best-practices/reliability/docs/application/#run-kubernetes-metrics-server"

    def check(self, resources: Resources):
        services = [i.metadata.name for i in resources.services]

        if "metrics-server" in services:
            self.result = Result(status=True, resource_type="Service")
        else:
            self.result = Result(
                status=False,
                resources=["metrics-server"],
                resource_type="Service",
            )


class check_vertical_pod_autoscaler_exists(Rule):
    _type = "cluster_wide"
    pillar = "reliability"
    section = "applications"
    message = "Deploy Vertical Pod Autoscaler."
    url = "https://aws.github.io/aws-eks-best-practices/reliability/docs/application/#run-kubernetes-metrics-server"

    def check(self, resources: Resources):
        deployments = [i.metadata.name for i in resources.deployments]

        if "vpa-recommender" in deployments:
            self.result = Result(status=True, resource_type="Deployment")
        else:
            self.result = Result(
                status=False,
                resources=["vpa-recommender"],
                resource_type="Deployment",
            )
