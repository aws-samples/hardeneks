from hardeneks.rules import Rule, Result
from ...resources import NamespacedResources


class disallow_container_socket_mount(Rule):
    _type = "namespace_based"
    pillar = "security"
    section = "pod_security"
    message = "Container socket mounts are not allowed."
    url = "https://aws.github.io/aws-eks-best-practices/security/docs/pods/#never-run-docker-in-docker-or-mount-the-socket-in-the-container"

    def check(self, namespaced_resources: NamespacedResources):
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


class disallow_host_path_or_make_it_read_only(Rule):
    _type = "namespace_based"
    pillar = "security"
    section = "pod_security"
    message = "Restrict the use of hostpath."
    url = "https://aws.github.io/aws-eks-best-practices/security/docs/pods/#restrict-the-use-of-hostpath-or-if-hostpath-is-necessary-restrict-which-prefixes-can-be-used-and-configure-the-volume-as-read-only"

    def check(self, namespaced_resources: NamespacedResources):

        offenders = []

        for pod in namespaced_resources.pods:
            for volume in pod.spec.volumes:
                if volume.host_path:
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


class set_requests_limits_for_containers(Rule):
    _type = "namespace_based"
    pillar = "security"
    section = "pod_security"
    message = "Set requests and limits for each container."
    url = "https://aws.github.io/aws-eks-best-practices/security/docs/pods/#set-requests-and-limits-for-each-container-to-avoid-resource-contention-and-dos-attacks"

    def check(self, namespaced_resources: NamespacedResources):

        offenders = []

        for pod in namespaced_resources.pods:
            for container in pod.spec.containers:
                if not (
                    container.resources.limits and container.resources.requests
                ):
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


class disallow_privilege_escalation(Rule):
    _type = "namespace_based"
    pillar = "security"
    section = "pod_security"
    message = "Set allowPrivilegeEscalation in the pod spec to false."
    url = "https://aws.github.io/aws-eks-best-practices/security/docs/pods/#do-not-allow-privileged-escalation"

    def check(self, namespaced_resources: NamespacedResources):

        offenders = []

        for pod in namespaced_resources.pods:
            for container in pod.spec.containers:
                if (
                    container.security_context
                    and container.security_context.allow_privilege_escalation
                ):
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


class check_read_only_root_file_system(Rule):
    _type = "namespace_based"
    pillar = "security"
    section = "pod_security"
    message = "Configure your images with a read-only root file system."
    url = "https://aws.github.io/aws-eks-best-practices/security/docs/pods/#configure-your-images-with-read-only-root-file-system"

    def check(self, namespaced_resources: NamespacedResources):

        offenders = []
        for pod in namespaced_resources.pods:
            for container in pod.spec.containers:
                if container.security_context is None:
                    offenders.append(pod)
                if (
                    container.security_context
                    and not container.security_context.read_only_root_filesystem
                ):
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
