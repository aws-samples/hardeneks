from kubernetes import client

from hardeneks.rules import Rule, Result
from hardeneks.resources import Resources


class check_metrics_server_is_running(Rule):
    _type = "cluster_wide"
    pillar = "reliability"
    section = "applications"
    message = "Metrics server is not deployed."
    url = "https://aws.github.io/aws-eks-best-practices/reliability/docs/application/#run-kubernetes-metrics-server"

    def check(self, resources: Resources):
        services = [
            i.metadata.name
            for i in client.CoreV1Api().list_service_for_all_namespaces().items
        ]

        if "metrics-server" in services:
            self.result = Result(status=True, resource_type="Service")
        else:
            self.result = Result(status=False, resource_type="Service")


class check_vertical_pod_autoscaler_exists(Rule):
    _type = "cluster_wide"
    pillar = "reliability"
    section = "applications"
    message = "Vertical pod autoscaler is not deployed."
    url = "https://aws.github.io/aws-eks-best-practices/reliability/docs/application/#run-kubernetes-metrics-server"

    def check(self, resources: Resources):

        deployments = [
            i.metadata.name
            for i in client.AppsV1Api()
            .list_deployment_for_all_namespaces()
            .items
        ]

        if "vpa-recommender" in deployments:
            self.result = Result(status=True, resource_type="Deployment")
        else:
            self.result = Result(status=False, resource_type="Deployment")
