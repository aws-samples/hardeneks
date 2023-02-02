import json
from pathlib import Path
from unittest.mock import patch

import kubernetes

from hardeneks.resources import Resources
from hardeneks.cluster_wide.cluster_autoscaling.cluster_autoscaler import (
    check_any_cluster_autoscaler_exists,
    ensure_cluster_autoscaler_and_cluster_versions_match,
    ensure_cluster_autoscaler_has_autodiscovery_mode,
    use_separate_iam_role_for_cluster_autoscaler,
    employ_least_privileged_access_cluster_autoscaler_role,
    use_managed_nodegroups,
)
from .conftest import get_response


def _read_json(file_path):
    with open(file_path) as f:
        json_content = json.load(f)
    return json_content


def _get_sample_data_path(directory, json_file):
    return Path.cwd() / "tests" / "data" / directory / json_file


@patch("kubernetes.client.AppsV1Api.list_deployment_for_all_namespaces")
def test_check_any_cluster_autoscaler_exists(mocked_client):

    test_data = (
        Path.cwd()
        / "tests"
        / "data"
        / "check_any_cluster_autoscaler_exists"
        / "cluster"
        / "deployments_api_response.json"
    )
    mocked_client.return_value = get_response(
        kubernetes.client.AppsV1Api,
        test_data,
        "V1DeploymentList",
    )
    resources = Resources("some_region", "some_context", "some_cluster", [])

    assert not check_any_cluster_autoscaler_exists(resources)


@patch("boto3.client")
@patch("kubernetes.client.AppsV1Api.list_deployment_for_all_namespaces")
def test_ensure_cluster_autoscaler_and_cluster_versions_match(
    mocked_k8s_client, mocked_boto_client
):

    test_data = (
        Path.cwd()
        / "tests"
        / "data"
        / "ensure_cluster_autoscaler_and_cluster_versions_match"
        / "cluster"
        / "deployments_api_response.json"
    )
    mocked_k8s_client.return_value = get_response(
        kubernetes.client.AppsV1Api,
        test_data,
        "V1DeploymentList",
    )

    mocked_boto_client.return_value.describe_cluster.return_value = {
        "cluster": {"version": "1.23"}
    }
    resources = Resources("some_region", "some_context", "some_cluster", [])

    assert not ensure_cluster_autoscaler_and_cluster_versions_match(resources)


@patch("kubernetes.client.AppsV1Api.list_deployment_for_all_namespaces")
def test_ensure_cluster_autoscaler_has_autodiscovery_mode(mocked_client):

    test_data = (
        Path.cwd()
        / "tests"
        / "data"
        / "ensure_cluster_autoscaler_has_autodiscovery_mode"
        / "cluster"
        / "deployments_api_response.json"
    )
    mocked_client.return_value = get_response(
        kubernetes.client.AppsV1Api,
        test_data,
        "V1DeploymentList",
    )
    resources = Resources("some_region", "some_context", "some_cluster", [])

    assert not ensure_cluster_autoscaler_has_autodiscovery_mode(resources)


@patch("kubernetes.client.AppsV1Api.list_deployment_for_all_namespaces")
@patch("kubernetes.client.CoreV1Api.read_namespaced_service_account")
def test_use_separate_iam_role_for_cluster_autoscaler(
    sa_client, deployment_client
):

    deployment_data = (
        Path.cwd()
        / "tests"
        / "data"
        / "use_separate_iam_role_for_cluster_autoscaler"
        / "cluster"
        / "deployments_api_response.json"
    )
    sa_data = (
        Path.cwd()
        / "tests"
        / "data"
        / "use_separate_iam_role_for_cluster_autoscaler"
        / "cluster"
        / "service_accounts_api_response.json"
    )
    deployment_client.return_value = get_response(
        kubernetes.client.AppsV1Api,
        deployment_data,
        "V1DeploymentList",
    )
    sa_return_value = get_response(
        kubernetes.client.CoreV1Api, sa_data, "V1ServiceAccount"
    )
    sa_client.return_value = sa_return_value

    resources = Resources("some_region", "some_context", "some_cluster", [])

    assert not use_separate_iam_role_for_cluster_autoscaler(resources)


@patch("boto3.client")
@patch("kubernetes.client.AppsV1Api.list_deployment_for_all_namespaces")
@patch("kubernetes.client.CoreV1Api.read_namespaced_service_account")
def test_employ_least_privileged_access_cluster_autoscaler_role(
    mocked_sa_client, mocked_deployment_client, mocked_boto_client
):

    deployment_data = (
        Path.cwd()
        / "tests"
        / "data"
        / "employ_least_privileged_access_cluster_autoscaler_role"
        / "cluster"
        / "deployments_api_response.json"
    )
    mocked_deployment_client.return_value = get_response(
        kubernetes.client.AppsV1Api,
        deployment_data,
        "V1DeploymentList",
    )
    sa_data = (
        Path.cwd()
        / "tests"
        / "data"
        / "employ_least_privileged_access_cluster_autoscaler_role"
        / "cluster"
        / "service_accounts_api_response.json"
    )
    sa_return_value = get_response(
        kubernetes.client.CoreV1Api, sa_data, "V1ServiceAccount"
    )
    mocked_sa_client.return_value = sa_return_value

    mocked_boto_client.return_value.get_policy_version.return_value = (
        _read_json(
            _get_sample_data_path(
                "employ_least_privileged_access_cluster_autoscaler_role",
                "get_policy_version.json",
            )
        )
    )

    mocked_boto_client.return_value.get_policy.return_value = _read_json(
        _get_sample_data_path(
            "employ_least_privileged_access_cluster_autoscaler_role",
            "get_policy.json",
        )
    )

    mocked_boto_client.return_value.get_role_policy.return_value = _read_json(
        _get_sample_data_path(
            "employ_least_privileged_access_cluster_autoscaler_role",
            "get_role_policy.json",
        )
    )

    mocked_boto_client.return_value.list_attached_role_policies.return_value = _read_json(
        _get_sample_data_path(
            "employ_least_privileged_access_cluster_autoscaler_role",
            "list_attached_role_policies.json",
        )
    )

    mocked_boto_client.return_value.list_role_policies.return_value = (
        _read_json(
            _get_sample_data_path(
                "employ_least_privileged_access_cluster_autoscaler_role",
                "list_role_policies.json",
            )
        )
    )

    resources = Resources("some_region", "some_context", "some_cluster", [])

    assert not employ_least_privileged_access_cluster_autoscaler_role(
        resources
    )


@patch("kubernetes.client.CoreV1Api.list_node")
def test_use_managed_nodegroups(mocked_client):

    test_data = (
        Path.cwd()
        / "tests"
        / "data"
        / "use_managed_nodegroups"
        / "cluster"
        / "nodes_api_response.json"
    )
    mocked_client.return_value = get_response(
        kubernetes.client.CoreV1Api,
        test_data,
        "V1NodeList",
    )
    resources = Resources("some_region", "some_context", "some_cluster", [])

    not_managed = [i.metadata.name for i in use_managed_nodegroups(resources)]

    assert not_managed == [
        "ip-192-168-59-44.ec2.internal",
        "ip-192-168-6-151.ec2.internal",
    ]
