from collections import Counter

from rich.console import Console

from ..resources import NamespacedResources
from ..report import (
    print_role_table,
    print_pod_table,
    print_workload_table,
)


console = Console()


def restrict_wildcard_for_roles(resources: NamespacedResources):
    offenders = []

    for role in resources.roles:
        for rule in role.rules:
            if "*" in rule.verbs:
                offenders.append(role)
            if "*" in rule.resources:
                offenders.append(role)

    if offenders:
        print_role_table(
            offenders,
            "Roles should not have '*' in Verbs or Resources",
            "Role",
        )
    return offenders


def disable_service_account_token_mounts(resources: NamespacedResources):
    offenders = []

    for pod in resources.pods:
        if pod.spec.automount_service_account_token:
            offenders.append(pod)

    if offenders:
        print_pod_table(
            offenders, "Auto-mounting of Service Account tokens is not allowed"
        )
    return offenders


def disable_run_as_root_user(resources: NamespacedResources):
    offenders = []

    for pod in resources.pods:
        security_context = pod.spec.security_context
        if (
            not security_context.run_as_group
            and not security_context.run_as_user
        ):
            offenders.append(pod)

    if offenders:
        print_pod_table(offenders, "Running as root is not allowed")

    return offenders


def disable_anonymous_access_for_roles(resources: NamespacedResources):
    offenders = []

    for role_binding in resources.role_bindings:
        if role_binding.subjects:
            for subject in role_binding.subjects:
                if (
                    subject.name == "system:unauthenticated"
                    or subject.name == "system:anonymous"
                ):
                    offenders.append(role_binding)

    if offenders:
        print_role_table(
            offenders,
            "Don't bind roles to anonymous or unauthenticated groups",
            "RoleBinding",
        )
    return offenders


def use_dedicated_service_accounts_for_each_deployment(
    resources: NamespacedResources,
):
    offenders = []

    count = Counter(
        [
            i.spec.template.spec.service_account_name
            for i in resources.deployments
        ]
    )
    repeated_service_accounts = {
        x: count for x, count in count.items() if count > 1
    }

    for k, v in repeated_service_accounts.items():
        for deployment in resources.deployments:
            if k == deployment.spec.template.spec.service_account_name:
                offenders.append(deployment)

    if offenders:
        print_workload_table(
            offenders,
            "Don't share service accounts between Deployments",
            "Deployment",
        )

    return offenders


def use_dedicated_service_accounts_for_each_stateful_set(
    resources: NamespacedResources,
):
    offenders = []

    count = Counter(
        [
            i.spec.template.spec.service_account_name
            for i in resources.stateful_sets
        ]
    )
    repeated_service_accounts = {
        x: count for x, count in count.items() if count > 1
    }

    for k, v in repeated_service_accounts.items():
        for deployment in resources.stateful_sets:
            if k == deployment.spec.template.spec.service_account_name:
                offenders.append(deployment)

    if offenders:
        print_workload_table(
            offenders,
            "Don't share service accounts between StatefulSets",
            "StatefulSet",
        )

    return offenders


def use_dedicated_service_accounts_for_each_daemon_set(
    resources: NamespacedResources,
):
    offenders = []

    count = Counter(
        [
            i.spec.template.spec.service_account_name
            for i in resources.daemon_sets
        ]
    )
    repeated_service_accounts = {
        x: count for x, count in count.items() if count > 1
    }

    for k, v in repeated_service_accounts.items():
        for deployment in resources.daemon_sets:
            if k == deployment.spec.template.spec.service_account_name:
                offenders.append(deployment)

    if offenders:
        print_workload_table(
            offenders,
            "Don't share service accounts between DaemonSets",
            "DaemonSet",
        )

    return offenders
