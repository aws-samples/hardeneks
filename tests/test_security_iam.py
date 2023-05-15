import json
from pathlib import Path
from unittest.mock import patch

import kubernetes
import pytest

from hardeneks.resources import NamespacedResources

from hardeneks.cluster_wide.security.iam import (
    restrict_wildcard_for_cluster_roles,
    check_endpoint_public_access,
    check_access_to_instance_profile,
    check_aws_node_daemonset_service_account,
    disable_anonymous_access_for_cluster_roles,
)
from hardeneks.namespace_based.security.iam import (
    restrict_wildcard_for_roles,
    disable_service_account_token_mounts,
    disable_run_as_root_user,
    disable_anonymous_access_for_roles,
    use_dedicated_service_accounts_for_each_daemon_set,
    use_dedicated_service_accounts_for_each_deployment,
    use_dedicated_service_accounts_for_each_stateful_set,
)
from .conftest import get_response


def read_json(file_path):
    with open(file_path) as f:
        json_content = json.load(f)
    return json_content


@pytest.mark.parametrize(
    "namespaced_resources",
    [("restrict_wildcard_for_roles")],
    indirect=["namespaced_resources"],
)
def test_restrict_wildcard_for_roles(namespaced_resources):
    rule = restrict_wildcard_for_roles()
    rule.check(namespaced_resources)

    assert "good" not in rule.result.resources
    assert "bad" in rule.result.resources


@pytest.mark.parametrize(
    "namespaced_resources",
    [("restrict_wildcard_for_cluster_roles")],
    indirect=["namespaced_resources"],
)
def test_restrict_wildcard_for_cluster_roles(namespaced_resources):
    rule = restrict_wildcard_for_cluster_roles()
    rule.check(namespaced_resources)

    assert "good" not in rule.result.resources
    assert "bad" in rule.result.resources


@patch("boto3.client")
def test_check_endpoint_public_access(mocked_client):
    namespaced_resources = NamespacedResources(
        "some_region", "some_context", "some_cluster", "some_ns"
    )

    test_data = (
        Path.cwd()
        / "tests"
        / "data"
        / "check_endpoint_public_access"
        / "cluster_metadata.json"
    )

    mocked_client.return_value.describe_cluster.return_value = read_json(
        test_data
    )
    rule = check_endpoint_public_access()
    rule.check(namespaced_resources)
    assert not rule.result.status


@patch("boto3.client")
def test_check_access_to_instance_profile(mocked_client):
    namespaced_resources = NamespacedResources(
        "some_region", "some_context", "some_cluster", "some_ns"
    )

    test_data = (
        Path.cwd()
        / "tests"
        / "data"
        / "check_access_to_instance_profile"
        / "instance_metadata.json"
    )

    mocked_client.return_value.describe_instances.return_value = read_json(
        test_data
    )
    rule = check_access_to_instance_profile()
    rule.check(namespaced_resources)
    resources = rule.result.resources
    assert len(resources) == 2


@patch("kubernetes.client.AppsV1Api.read_namespaced_daemon_set")
@patch("kubernetes.client.CoreV1Api.read_namespaced_service_account")
def test_check_aws_node_daemonset_service_account(
    mocked_core_api, mocked_apps_api
):
    daemon_set_data = (
        Path.cwd()
        / "tests"
        / "data"
        / "check_aws_node_daemonset_service_account"
        / "daemon_sets_api_response.json"
    )
    service_account_data = (
        Path.cwd()
        / "tests"
        / "data"
        / "check_aws_node_daemonset_service_account"
        / "service_accounts_api_response.json"
    )
    mocked_apps_api.return_value = get_response(
        kubernetes.client.AppsV1Api,
        daemon_set_data,
        "V1DaemonSet",
    )
    mocked_core_api.return_value = get_response(
        kubernetes.client.CoreV1Api, service_account_data, "V1ServiceAccount"
    )
    namespaced_resources = NamespacedResources(
        "some_region", "some_context", "some_cluster", "some_ns"
    )
    rule = check_aws_node_daemonset_service_account()
    rule.check(namespaced_resources)

    assert not rule.result.status


@pytest.mark.parametrize(
    "namespaced_resources",
    [("disable_service_account_token_mounts")],
    indirect=["namespaced_resources"],
)
def test_disable_service_account_token_mounts(namespaced_resources):
    rule = disable_service_account_token_mounts()
    rule.check(namespaced_resources)

    assert "good" not in rule.result.resources
    assert "bad" in rule.result.resources


@pytest.mark.parametrize(
    "namespaced_resources",
    [("disable_run_as_root_user")],
    indirect=["namespaced_resources"],
)
def test_disable_run_as_root_user(namespaced_resources):
    rule = disable_run_as_root_user()

    rule.check(namespaced_resources)

    assert "good" not in rule.result.resources
    assert "bad" in rule.result.resources


@pytest.mark.parametrize(
    "namespaced_resources",
    [("disable_anonymous_access_for_cluster_roles")],
    indirect=["namespaced_resources"],
)
def test_disable_anonymous_access_for_cluster_roles(namespaced_resources):
    rule = disable_anonymous_access_for_cluster_roles()
    rule.check(namespaced_resources)
    assert "system:public-info-viewer" not in rule.result.resources
    assert "good" not in rule.result.resources
    assert "bad" in rule.result.resources


@pytest.mark.parametrize(
    "namespaced_resources",
    [("disable_anonymous_access_for_roles")],
    indirect=["namespaced_resources"],
)
def test_disable_anonymous_access_for_roles(namespaced_resources):
    rule = disable_anonymous_access_for_roles()

    rule.check(namespaced_resources)

    assert "good" not in rule.result.resources
    assert "bad" in rule.result.resources


@pytest.mark.parametrize(
    "namespaced_resources",
    [("use_dedicated_service_accounts_for_each_daemon_set")],
    indirect=["namespaced_resources"],
)
def test_use_dedicated_service_accounts_for_each_daemon_set(
    namespaced_resources,
):
    rule = use_dedicated_service_accounts_for_each_daemon_set()
    rule.check(namespaced_resources)

    assert "shared-sa-1" in rule.result.resources
    assert "shared-sa-2" in rule.result.resources


@pytest.mark.parametrize(
    "namespaced_resources",
    [("use_dedicated_service_accounts_for_each_deployment")],
    indirect=["namespaced_resources"],
)
def test_use_dedicated_service_accounts_for_each_deployment(
    namespaced_resources,
):
    rule = use_dedicated_service_accounts_for_each_deployment()
    rule.check(namespaced_resources)

    assert "shared-sa-1" in rule.result.resources
    assert "shared-sa-2" in rule.result.resources


@pytest.mark.parametrize(
    "namespaced_resources",
    [("use_dedicated_service_accounts_for_each_stateful_set")],
    indirect=["namespaced_resources"],
)
def test_use_dedicated_service_accounts_for_each_stateful_set(
    namespaced_resources,
):
    rule = use_dedicated_service_accounts_for_each_stateful_set()
    rule.check(namespaced_resources)
    assert "shared-sa-1" in rule.result.resources
    assert "shared-sa-2" in rule.result.resources
