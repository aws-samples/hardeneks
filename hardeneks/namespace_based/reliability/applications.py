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
            offenders, "[red]Avoid running pods without deployments."
        )
    return offenders


def run_multiple_replicas(namespaced_resources: NamespacedResources):
    offenders = []

    for deployment in namespaced_resources.deployments:
        if deployment.spec.replicas < 2:
            offenders.append(deployment)

    if offenders:
        print_deployment_table(
            offenders, "[red]Avoid running single replica deployments"
        )
    return offenders


def schedule_replicas_across_nodes(namespaced_resources: NamespacedResources):
    offenders = []

    for deployment in namespaced_resources.deployments:
        affinity = deployment.spec.template.spec.affinity
        if not affinity:
            offenders.append(deployment)
        elif affinity and affinity.node_affinity:
            node_selectors = (
                affinity.node_affinity.required_during_scheduling_ignored_during_execution.node_selector_terms  # noqa: E501
            )
            expressions = [i.match_expressions for i in node_selectors]
            keys = set([i[0].key for i in expressions])
            if not set(
                ["topology.kubernetes.io/zone", "kubernetes.io/hostname"]
            ).issubset(keys):
                offenders.append(deployment)

    if offenders:
        print_service_table(
            offenders, "[red]Spread replicas across AZs and Nodes"
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
            offenders, "[red]Deploy horizontal pod autoscaler for deployments"
        )
    return offenders
