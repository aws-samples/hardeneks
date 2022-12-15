from rich.console import Console

from ...report import (
    print_pod_table,
)
from ...resources import NamespacedResources


console = Console()


def disallow_container_socket_mount(namespaced_resources: NamespacedResources):
    offenders = []

    sockets = [
        "/var/run/docker.sock",
        "/var/run/containerd.sock",
        "/var/run/crio.sock",
    ]

    for pod in namespaced_resources.pods:
        for volume in pod.spec.volumes:
            if volume.host_path and volume.host_path.path in sockets:
                offenders.append(pod)

    if offenders:
        print_pod_table(
            offenders,
            "[red]Container socket mounts are not allowed",
            "[link=https://aws.github.io/aws-eks-best-practices/security/docs/pods/#never-run-docker-in-docker-or-mount-the-socket-in-the-container]Click to see the guide[/link]",
        )

    return offenders


def disallow_host_path_or_make_it_read_only(
    namespaced_resources: NamespacedResources,
):
    offenders = []

    for pod in namespaced_resources.pods:
        for volume in pod.spec.volumes:
            if volume.host_path:
                offenders.append(pod)

    if offenders:
        print_pod_table(
            offenders,
            "[red]Restrict the use of hostpath.",
            "[link=https://aws.github.io/aws-eks-best-practices/security/docs/pods/#restrict-the-use-of-hostpath-or-if-hostpath-is-necessary-restrict-which-prefixes-can-be-used-and-configure-the-volume-as-read-only]Click to see the guide[/link]",
        )

    return offenders


def set_requests_limits_for_containers(
    namespaced_resources: NamespacedResources,
):
    offenders = []

    for pod in namespaced_resources.pods:
        for container in pod.spec.containers:
            if not (
                container.resources.limits and container.resources.requests
            ):
                offenders.append(pod)

    if offenders:
        print_pod_table(
            offenders,
            "[red]Set requests and limits for each container.",
            "[link=https://aws.github.io/aws-eks-best-practices/security/docs/pods/#set-requests-and-limits-for-each-container-to-avoid-resource-contention-and-dos-attacks]Click to see the guide[/link]",
        )

    return offenders


def disallow_privilege_escalation(namespaced_resources: NamespacedResources):
    offenders = []

    for pod in namespaced_resources.pods:
        for container in pod.spec.containers:
            if (
                container.security_context
                and container.security_context.allow_privilege_escalation
            ):
                offenders.append(pod)

    if offenders:
        print_pod_table(
            offenders,
            "[red]Set allowPrivilegeEscalation in the pod spec to false",
            "[link=https://aws.github.io/aws-eks-best-practices/security/docs/pods/#do-not-allow-privileged-escalation]Click to see the guide[/link]",
        )

    return offenders


def check_read_only_root_file_system(
    namespaced_resources: NamespacedResources,
):
    offenders = []
    for pod in namespaced_resources.pods:
        for container in pod.spec.containers:
            if (
                container.security_context
                and not container.security_context.read_only_root_filesystem
            ):
                offenders.append(pod)
    if offenders:
        print_pod_table(
            offenders,
            "[red]Configure your images with a read-only root file system",
            "[link=https://aws.github.io/aws-eks-best-practices/security/docs/pods/#configure-your-images-with-read-only-root-file-system]Click to see the guide[/link]",
        )

    return offenders
