from pathlib import Path
from unittest.mock import patch

import kubernetes

from hardeneks.resources import Resources
from hardeneks.cluster_wide.cluster_autoscaling.cluster_autoscaler import (
    check_any_cluster_autoscaler_exists,
    ensure_cluster_autoscaler_and_cluster_versions_match,
)
from .conftest import get_response


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
def test_ensure_cluster_autoscaler_and_cluster_versions_matchs(
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
