from collections import Counter

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
                if "*" in rule.verbs:
                    offenders.append(role)
                if "*" in rule.resources:
                    offenders.append(role)

        self.result = Result(
            status=True,
            resource_type="Role",
            namespace=namespaced_resources.namespace,
        )
        if offenders:
            self.result = Result(
                status=False,
                resource_type="Role",
                resources=[i.metadata.name for i in offenders],
                namespace=namespaced_resources.namespace,
            )


class disable_service_account_token_mounts(Rule):
    _type = "namespace_based"
    pillar = "security"
    section = "iam"
    message = "Auto-mounting of Service Account tokens is not allowed."
    url = "https://aws.github.io/aws-eks-best-practices/security/docs/iam/#disable-auto-mounting-of-service-account-tokens"

    def check(self, namespaced_resources: NamespacedResources):

        offenders = []

        for pod in namespaced_resources.pods:
            if pod.spec.automount_service_account_token:
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


class disable_run_as_root_user(Rule):
    _type = "namespace_based"
    pillar = "security"
    section = "iam"
    message = "Running as root is not allowed."
    url = "https://aws.github.io/aws-eks-best-practices/security/docs/iam/#run-the-application-as-a-non-root-user"

    def check(self, namespaced_resources: NamespacedResources):

        offenders = []

        for pod in namespaced_resources.pods:
            security_context = pod.spec.security_context
            containers = pod.spec.containers
            
            if (
                not security_context.run_as_group
                and not security_context.run_as_user
            ):
                for con in containers:
                    security_context = con.security_context
                    try:
                        run_as_group = security_context.run_as_group
                        run_as_user = security_context.run_as_user
                    except AttributeError:
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
                        offenders.append(role_binding)

        self.result = Result(
            status=True,
            resource_type="RoleBinding",
            namespace=namespaced_resources.namespace,
            )
        if offenders:
            self.result = Result(
                status=False,
                resource_type="RoleBinding",
                resources=[i.metadata.name for i in offenders],
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

        for k, v in repeated_service_accounts.items():
            for deployment in namespaced_resources.deployments:
                if k == deployment.spec.template.spec.service_account_name:
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


class use_dedicated_service_accounts_for_each_stateful_set(
    Rule,
):
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

        for k, v in repeated_service_accounts.items():
            for deployment in namespaced_resources.stateful_sets:
                if k == deployment.spec.template.spec.service_account_name:
                    offenders.append(deployment)

        self.result = Result(
            status=True,
            resource_type="StatefulSet",
            namespace=namespaced_resources.namespace,
            )
        if offenders:
            self.result = Result(
                status=False,
                resource_type="StatefulSet",
                resources=[i.metadata.name for i in offenders],
                namespace=namespaced_resources.namespace,
            )


class use_dedicated_service_accounts_for_each_daemon_set(
    Rule,
):
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

        for k, v in repeated_service_accounts.items():
            for deployment in namespaced_resources.daemon_sets:
                if k == deployment.spec.template.spec.service_account_name:
                    offenders.append(deployment)

        self.result = Result(
            status=True, 
            resource_type="DaemonSet",
            namespace=namespaced_resources.namespace,
            )
        if offenders:
            self.result = Result(
                status=False,
                resource_type="DaemonSet",
                resources=[i.metadata.name for i in offenders],
                namespace=namespaced_resources.namespace,
            )
