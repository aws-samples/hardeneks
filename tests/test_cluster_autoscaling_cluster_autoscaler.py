import json
from pathlib import Path
from unittest.mock import patch

import kubernetes
import pytest

from hardeneks.resources import Resources
from .conftest import get_response
from hardeneks.cluster_wide.cluster_autoscaling.cluster_autoscaler import (
    check_any_cluster_autoscaler_exists,
    ensure_cluster_autoscaler_and_cluster_versions_match,
    ensure_cluster_autoscaler_has_autodiscovery_mode,
    use_separate_iam_role_for_cluster_autoscaler,
    employ_least_privileged_access_cluster_autoscaler_role,
    use_managed_nodegroups,
)


def _read_json(file_path):
    with open(file_path) as f:
        json_content = json.load(f)
    return json_content


def _get_sample_data_path(directory, json_file):
    return Path.cwd() / "tests" / "data" / directory / json_file


@pytest.mark.parametrize(
    "resources",
    [(("check_any_cluster_autoscaler_exists", ["deployments"]))],
    indirect=["resources"],
)
def test_check_any_cluster_autoscaler_exists(resources):
    rule = check_any_cluster_autoscaler_exists()
    rule.check(resources)

    assert not rule.result.status


@pytest.mark.parametrize(
    "resources",
    [(("ensure_cluster_autoscaler_and_cluster_versions_match", ["deployments"]))],
    indirect=["resources"],
)
@patch("boto3.client")
def test_ensure_cluster_autoscaler_and_cluster_versions_match(
    mocked_boto_client, resources
):
    mocked_boto_client.return_value.describe_cluster.return_value = {
        "cluster": {"version": "1.23"}
    }
    rule = ensure_cluster_autoscaler_and_cluster_versions_match()
    rule.check(resources)

    assert not rule.result.status


@pytest.mark.parametrize(
    "resources",
    [(("ensure_cluster_autoscaler_has_autodiscovery_mode", ["deployments"]))],
    indirect=["resources"],
)
def test_ensure_cluster_autoscaler_has_autodiscovery_mode(resources):
    rule = ensure_cluster_autoscaler_has_autodiscovery_mode()
    rule.check(resources)
    assert not rule.result.status


@pytest.mark.parametrize(
    "resources",
    [(("use_separate_iam_role_for_cluster_autoscaler", ["deployments"]))],
    indirect=["resources"],
)
@patch("kubernetes.client.CoreV1Api.read_namespaced_service_account")
def test_use_separate_iam_role_for_cluster_autoscaler(mock_read_sa, resources):
    sa_data = (
        Path.cwd()
        / "tests"
        / "data"
        / "use_separate_iam_role_for_cluster_autoscaler"
        / "cluster"
        / "serviceaccount_api_response.json"
    )
    mock_read_sa.return_value = get_response(
        kubernetes.client.CoreV1Api, sa_data, "V1ServiceAccount"
    )
    rule = use_separate_iam_role_for_cluster_autoscaler()
    rule.check(resources)
    assert not rule.result.status


@pytest.mark.parametrize(
    "resources",
    [(("employ_least_privileged_access_cluster_autoscaler_role", ["deployments"]))],
    indirect=["resources"],
)
@patch("kubernetes.client.CoreV1Api.read_namespaced_service_account")
@patch("boto3.client")
def test_employ_least_privileged_access_cluster_autoscaler_role(
    mocked_boto_client, mock_read_sa, resources
):
    sa_data = (
        Path.cwd()
        / "tests"
        / "data"
        / "employ_least_privileged_access_cluster_autoscaler_role"
        / "cluster"
        / "serviceaccount_api_response.json"
    )
    mock_read_sa.return_value = get_response(
        kubernetes.client.CoreV1Api, sa_data, "V1ServiceAccount"
    )
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

    rule = employ_least_privileged_access_cluster_autoscaler_role()
    rule.check(resources)

    assert not rule.result.status


@pytest.mark.parametrize(
    "resources",
    [(("use_managed_nodegroups", ["nodes"]))],
    indirect=["resources"],
)
def test_use_managed_nodegroups(resources):
    rule = use_managed_nodegroups()
    rule.check(resources)

    assert rule.result.resources == [
        "ip-192-168-59-44.ec2.internal",
        "ip-192-168-6-151.ec2.internal",
    ]
