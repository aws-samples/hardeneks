from ...resources import NamespacedResources


from ...report import (
    print_pod_table,
    print_service_table,
    print_deployment_table,
)


def avoid_running_singleton_pods(namespaced_resources: NamespacedResources):
    offenders = []
    for pod in namespaced_resources.pods:
        owner = pod.metadata.owner_references
        if not owner:
            offenders.append(pod)

    if offenders:
        print_pod_table(
            offenders,
            "[red]Avoid running pods without deployments.",
            "[link=https://aws.github.io/aws-eks-best-practices/reliability/docs/application/#avoid-running-singleton-pods]Click to see the guide[/link]",
        )
    return offenders


def run_multiple_replicas(namespaced_resources: NamespacedResources):
    offenders = []

    for deployment in namespaced_resources.deployments:
        if deployment.spec.replicas < 2:
            offenders.append(deployment)

    if offenders:
        print_deployment_table(
            offenders,
            "[red]Avoid running single replica deployments",
            "[link=https://aws.github.io/aws-eks-best-practices/reliability/docs/application/#run-multiple-replicas]Click to see the guide[/link]",
        )
    return offenders


def schedule_replicas_across_nodes(namespaced_resources: NamespacedResources):
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

    if offenders:
        print_service_table(
            offenders,
            "[red]Spread replicas across AZs and Nodes",
            "[link=https://aws.github.io/aws-eks-best-practices/reliability/docs/application/#schedule-replicas-across-nodes]Click to see the guide[/link]",
        )
    return offenders


def check_horizontal_pod_autoscaling_exists(
    namespaced_resources: NamespacedResources,
):
    offenders = []

    hpas = [i.spec.scale_target_ref.name for i in namespaced_resources.hpas]

    for deployment in namespaced_resources.deployments:
        if deployment.metadata.name not in hpas:
            offenders.append(deployment)

    if offenders:
        print_service_table(
            offenders,
            "[red]Deploy horizontal pod autoscaler for deployments",
            "[link=https://aws.github.io/aws-eks-best-practices/reliability/docs/application/#horizontal-pod-autoscaler-hpa]Click to see the guide[/link]",
        )
    return offenders


def check_readiness_probes(namespaced_resources: NamespacedResources):
    offenders = []

    for pod in namespaced_resources.pods:
        for container in pod.spec.containers:
            if not container.readiness_probe:
                offenders.append(pod)

    if offenders:
        print_pod_table(
            offenders,
            "[red]Define readiness probes for pods.",
            "[link=https://aws.github.io/aws-eks-best-practices/reliability/docs/application/#use-readiness-probe-to-detect-partial-unavailability]Click to see the guide[/link]",
        )
    return offenders


def check_liveness_probes(namespaced_resources: NamespacedResources):
    offenders = []

    for pod in namespaced_resources.pods:
        for container in pod.spec.containers:
            if not container.liveness_probe:
                offenders.append(pod)

    if offenders:
        print_pod_table(
            offenders,
            "[red]Define liveness probes for pods.",
            "[link=https://aws.github.io/aws-eks-best-practices/reliability/docs/application/#use-liveness-probe-to-remove-unhealthy-pods]Click to see the guide[/link]",
        )
    return offenders
