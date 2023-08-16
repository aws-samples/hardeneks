from ...resources import NamespacedResources
from hardeneks.rules import Rule, Result


class avoid_running_singleton_pods(Rule):
    _type = "namespace_based"
    pillar = "reliability"
    section = "applications"
    message = "Avoid running pods without deployments."
    url = "https://aws.github.io/aws-eks-best-practices/reliability/docs/application/#avoid-running-singleton-pods"

    def check(self, namespaced_resources: NamespacedResources):
        offenders = []
        for pod in namespaced_resources.pods:
            owner = pod.metadata.owner_references
            if not owner:
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


class run_multiple_replicas(Rule):
    _type = "namespace_based"
    pillar = "reliability"
    section = "applications"
    message = "Avoid running single replica deployments."
    url = "https://aws.github.io/aws-eks-best-practices/reliability/docs/application/#run-multiple-replicas"

    def check(self, namespaced_resources: NamespacedResources):

        offenders = []

        for deployment in namespaced_resources.deployments:
            if deployment.spec.replicas < 2:
                offenders.append(deployment)

        self.result = Result(
            status=True, 
            resource_type="Deployment", 
            namespace=namespaced_resources.namespace
        )
        if offenders:
            self.result = Result(
                status=False,
                resource_type="Deployment",
                resources=[i.metadata.name for i in offenders],
                namespace=namespaced_resources.namespace,
            )


class schedule_replicas_across_nodes(Rule):
    _type = "namespace_based"
    pillar = "reliability"
    section = "applications"
    message = "Spread replicas across AZs and Nodes."
    url = "https://aws.github.io/aws-eks-best-practices/reliability/docs/application/#schedule-replicas-across-nodes"

    def check(self, namespaced_resources: NamespacedResources):

        offenders = []

        for deployment in namespaced_resources.deployments:
            spread = deployment.spec.template.spec.topology_spread_constraints
            if not spread:
                offenders.append(deployment)
            else:
                topology_keys = set([i.topology_key for i in spread])
                if not set(["topology.kubernetes.io/zone"]).issubset(
                    topology_keys
                ):
                    offenders.append(deployment)

        self.result = Result(
            status=True, 
            resource_type="Deployment", 
            namespace=namespaced_resources.namespace
        )
        if offenders:
            self.result = Result(
                status=False,
                resource_type="Deployment",
                resources=[i.metadata.name for i in offenders],
                namespace=namespaced_resources.namespace,
            )


class check_horizontal_pod_autoscaling_exists(Rule):
    _type = "namespace_based"
    pillar = "reliability"
    section = "applications"
    message = "Deploy horizontal pod autoscaler for deployments."
    url = "https://aws.github.io/aws-eks-best-practices/reliability/docs/application/#horizontal-pod-autoscaler-hpa"

    def check(self, namespaced_resources: NamespacedResources):

        offenders = []

        hpas = [
            i.spec.scale_target_ref.name for i in namespaced_resources.hpas
        ]

        for deployment in namespaced_resources.deployments:
            if deployment.metadata.name not in hpas:
                offenders.append(deployment)

        self.result = Result(
            status=True, 
            resource_type="Deployment",
            namespace=namespaced_resources.namespace,
        )
        if offenders:
            self.result = Result(
                status=False,
                resource_type="Deployment",
                resources=[i.metadata.name for i in offenders],
                namespace=namespaced_resources.namespace,
            )


class check_readiness_probes(Rule):
    _type = "namespace_based"
    pillar = "reliability"
    section = "applications"
    message = "Define readiness probes for pods."
    url = "https://aws.github.io/aws-eks-best-practices/reliability/docs/application/#use-readiness-probe-to-detect-partial-unavailability"

    def check(self, namespaced_resources: NamespacedResources):

        offenders = []

        for pod in namespaced_resources.pods:
            for container in pod.spec.containers:
                if not container.readiness_probe:
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


class check_liveness_probes(Rule):
    _type = "namespace_based"
    pillar = "reliability"
    section = "applications"
    message = "Define liveness probes for pods."
    url = "https://aws.github.io/aws-eks-best-practices/reliability/docs/application/#use-liveness-probe-to-remove-unhealthy-pods"

    def check(self, namespaced_resources: NamespacedResources):

        offenders = []

        for pod in namespaced_resources.pods:
            for container in pod.spec.containers:
                if not container.liveness_probe:
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
