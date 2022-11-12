import os

from kubernetes import client
import pytest

from hardeneks.resources import NamespacedResources


class Response:
    def __init__(self, filename):
        with open(filename) as file:
            self.data = file.read()


def get_response(api, _file, _class):
    return api().api_client.deserialize(
        Response(_file),
        _class,
    )


@pytest.fixture(scope="function")
def namespaced_resources(request):
    current_directory = os.path.dirname(__file__)
    data_directory = os.path.join(
        current_directory, "data", request.param, "cluster"
    )
    resources = NamespacedResources(
        "some_region", "some_context", "some_cluster", "some_namespace"
    )
    resources.namespaces = get_response(
        client.CoreV1Api,
        os.path.join(data_directory, "namespaces_api_response.json"),
        "V1NamespaceList",
    ).items
    resources.resource_quotas = get_response(
        client.CoreV1Api,
        os.path.join(data_directory, "resource_quotas_api_response.json"),
        "V1ResourceQuotaList",
    ).items
    resources.pods = get_response(
        client.CoreV1Api,
        os.path.join(data_directory, "pods_api_response.json"),
        "V1PodList",
    ).items
    resources.services = get_response(
        client.CoreV1Api,
        os.path.join(data_directory, "services_api_response.json"),
        "V1ServiceList",
    ).items
    resources.roles = get_response(
        client.RbacAuthorizationV1Api,
        os.path.join(data_directory, "roles_api_response.json"),
        "V1RoleList",
    ).items
    resources.cluster_roles = get_response(
        client.RbacAuthorizationV1Api,
        os.path.join(data_directory, "cluster_roles_api_response.json"),
        "V1ClusterRoleList",
    ).items
    resources.role_bindings = get_response(
        client.RbacAuthorizationV1Api,
        os.path.join(data_directory, "role_bindings_api_response.json"),
        "V1RoleBindingList",
    ).items
    resources.cluster_role_bindings = get_response(
        client.RbacAuthorizationV1Api,
        os.path.join(
            data_directory, "cluster_role_bindings_api_response.json"
        ),
        "V1ClusterRoleBindingList",
    ).items
    resources.daemon_sets = get_response(
        client.AppsV1Api,
        os.path.join(data_directory, "daemon_sets_api_response.json"),
        "V1DaemonSetList",
    ).items
    resources.stateful_sets = get_response(
        client.AppsV1Api,
        os.path.join(data_directory, "stateful_sets_api_response.json"),
        "V1StatefulSetList",
    ).items
    resources.deployments = get_response(
        client.AppsV1Api,
        os.path.join(data_directory, "deployments_api_response.json"),
        "V1DeploymentList",
    ).items
    resources.network_policies = get_response(
        client.NetworkingV1Api,
        os.path.join(data_directory, "network_policies_api_response.json"),
        "V1NetworkPolicyList",
    ).items
    resources.hpas = get_response(
        client.AutoscalingV1Api,
        os.path.join(
            data_directory, "horizontal_pod_autoscaler_api_response.json"
        ),
        "V1HorizontalPodAutoscalerList",
    ).items
    return resources
