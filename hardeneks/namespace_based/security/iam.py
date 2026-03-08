from collections import Counter

from kubernetes import client

from ...resources import NamespacedResources
from hardeneks.rules import Rule, Result


class restrict_wildcard_for_roles(Rule):
    _type = "namespace_based"
    pillar = "security"
    section = "iam"
    message = "Roles should not have '*' in Verbs or Resources."
    url = "https://aws.github.io/aws-eks-best-practices/security/docs/iam/#employ-least-privileged-access-when-creating-rolebindings-and-clusterrolebindings"

    def check(self, namespaced_resources: NamespacedResources):
        offenders = []

        for role in namespaced_resources.roles:
            for rule in role.rules:
                if rule.verbs and "*" in rule.verbs:
                    offenders.append(role.metadata.name)
                    break
                if rule.resources and "*" in rule.resources:
                    offenders.append(role.metadata.name)
                    break

        self.result = Result(
            status=True,
            resource_type="Role",
            namespace=namespaced_resources.namespace,
        )
        if offenders:
            self.result = Result(
                status=False,
                resource_type="Role",
                resources=offenders,
                namespace=namespaced_resources.namespace,
            )


class disable_service_account_token_mounts(Rule):
    _type = "namespace_based"
    pillar = "security"
    section = "iam"
    message = "Default service account should have automountServiceAccountToken set to false."
    url = "https://aws.github.io/aws-eks-best-practices/security/docs/iam/#disable-auto-mounting-of-service-account-tokens"

    def check(self, namespaced_resources: NamespacedResources):
        sa = client.CoreV1Api().read_namespaced_service_account(
            name="default", namespace=namespaced_resources.namespace
        )

        self.result = Result(
            status=True,
            resource_type="ServiceAccount",
            namespace=namespaced_resources.namespace,
        )
        if sa.automount_service_account_token != False:
            self.result = Result(
                status=False,
                resource_type="ServiceAccount",
                resources=["default"],
                namespace=namespaced_resources.namespace,
            )


class disable_run_as_root_user(Rule):
    _type = "namespace_based"
    pillar = "security"
    section = "iam"
    message = "Running as root is not allowed."
    url = "https://aws.github.io/aws-eks-best-practices/security/docs/iam/#run-the-application-as-a-non-root-user"

    def check(self, namespaced_resources: NamespacedResources):
        offenders = []

        for pod in namespaced_resources.pods:
            container_root_user = False
            # Check container-level security context first since it takes precedence.
            for container in pod.spec.containers:
                if not container.security_context or \
                    container.security_context.run_as_user in (None, 0) or \
                    container.security_context.run_as_group in (None, 0):
                    container_root_user = True
                    break
            # Check if pod-level security context is also not configured.
            if container_root_user and (not pod.spec.security_context or \
               pod.spec.security_context.run_as_user in (None, 0) or \
               pod.spec.security_context.run_as_group in (None, 0)):
                    offenders.append(pod.metadata.name)


        self.result = Result(
            status=True, 
            resource_type="Pod",
            namespace=namespaced_resources.namespace,
        )
        
        if offenders:
            self.result = Result(
                status=False,
                resource_type="Pod",
                resources=offenders,
                namespace=namespaced_resources.namespace,
            )


class disable_anonymous_access_for_roles(Rule):
    _type = "namespace_based"
    pillar = "security"
    section = "iam"
    message = "Don't bind roles to anonymous or unauthenticated groups."
    url = "https://aws.github.io/aws-eks-best-practices/security/docs/iam/#review-and-revoke-unnecessary-anonymous-access"

    def check(self, namespaced_resources: NamespacedResources):

        offenders = []

        for role_binding in namespaced_resources.role_bindings:
            if role_binding.subjects:
                for subject in role_binding.subjects:
                    if (
                        subject.name == "system:unauthenticated"
                        or subject.name == "system:anonymous"
                    ):
                        offenders.append(role_binding.metadata.name)
                        break

        self.result = Result(
            status=True,
            resource_type="RoleBinding",
            namespace=namespaced_resources.namespace,
            )
        if offenders:
            self.result = Result(
                status=False,
                resource_type="RoleBinding",
                resources=offenders,
                namespace=namespaced_resources.namespace,
            )


class use_dedicated_service_accounts_for_each_deployment(Rule):
    _type = "namespace_based"
    pillar = "security"
    section = "iam"
    message = "Don't share service accounts between Deployments."
    url = "https://aws.github.io/aws-eks-best-practices/security/docs/iam/#use-dedicated-service-accounts-for-each-application"

    def check(self, namespaced_resources: NamespacedResources):

        offenders = []

        count = Counter(
            [
                i.spec.template.spec.service_account_name
                for i in namespaced_resources.deployments
            ]
        )
        repeated_service_accounts = {
            x: count for x, count in count.items() if count > 1
        }

        for k, _ in repeated_service_accounts.items():
            for deployment in namespaced_resources.deployments:
                if k == deployment.spec.template.spec.service_account_name:
                    offenders.append(deployment.metadata.name)

        self.result = Result(
            status=True,
            resource_type="Deployment",
            namespace=namespaced_resources.namespace,
        )
        if offenders:
            self.result = Result(
                status=False,
                resource_type="Deployment",
                resources=offenders,
                namespace=namespaced_resources.namespace,
            )


class use_dedicated_service_accounts_for_each_stateful_set(Rule):
    _type = "namespace_based"
    pillar = "security"
    section = "iam"
    message = "Don't share service accounts between StatefulSets."
    url = "https://aws.github.io/aws-eks-best-practices/security/docs/iam/#use-dedicated-service-accounts-for-each-application"

    def check(self, namespaced_resources: NamespacedResources):

        offenders = []

        count = Counter(
            [
                i.spec.template.spec.service_account_name
                for i in namespaced_resources.stateful_sets
            ]
        )
        repeated_service_accounts = {
            x: count for x, count in count.items() if count > 1
        }

        for k, _ in repeated_service_accounts.items():
            for stateful_set in namespaced_resources.stateful_sets:
                if k == stateful_set.spec.template.spec.service_account_name:
                    offenders.append(stateful_set.metadata.name)

        self.result = Result(
            status=True,
            resource_type="StatefulSet",
            namespace=namespaced_resources.namespace,
            )
        if offenders:
            self.result = Result(
                status=False,
                resource_type="StatefulSet",
                resources=offenders,
                namespace=namespaced_resources.namespace,
            )


class use_dedicated_service_accounts_for_each_daemon_set(Rule):
    _type = "namespace_based"
    pillar = "security"
    section = "iam"
    message = "Don't share service accounts between DaemonSets."
    url = "https://aws.github.io/aws-eks-best-practices/security/docs/iam/#use-dedicated-service-accounts-for-each-application"

    def check(self, namespaced_resources: NamespacedResources):

        offenders = []

        count = Counter(
            [
                i.spec.template.spec.service_account_name
                for i in namespaced_resources.daemon_sets
            ]
        )
        repeated_service_accounts = {
            x: count for x, count in count.items() if count > 1
        }

        for k, _ in repeated_service_accounts.items():
            for daemon_set in namespaced_resources.daemon_sets:
                if k == daemon_set.spec.template.spec.service_account_name:
                    offenders.append(daemon_set.metadata.name)

        self.result = Result(
            status=True, 
            resource_type="DaemonSet",
            namespace=namespaced_resources.namespace,
            )
        if offenders:
            self.result = Result(
                status=False,
                resource_type="DaemonSet",
                resources=offenders,
                namespace=namespaced_resources.namespace,
            )
