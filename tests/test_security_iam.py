import json
from pathlib import Path
from unittest.mock import patch

import kubernetes
import pytest

from hardeneks.resources import NamespacedResources

from hardeneks.security.iam import (
    restrict_wildcard_for_roles,
    restrict_wildcard_for_cluster_roles,
    check_endpoint_public_access,
    check_access_to_instance_profile,
    check_aws_node_daemonset_service_account,
    disable_service_account_token_mounts,
    disable_run_as_root_user,
    disable_anonymous_access_for_cluster_roles,
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
    offenders = restrict_wildcard_for_roles(namespaced_resources)

    assert "good" not in [i.metadata.name for i in offenders]
    assert "bad" in [i.metadata.name for i in offenders]


@pytest.mark.parametrize(
    "namespaced_resources",
    [("restrict_wildcard_for_cluster_roles")],
    indirect=["namespaced_resources"],
)
def test_restrict_wildcard_for_cluster_roles(namespaced_resources):
    offenders = restrict_wildcard_for_cluster_roles(namespaced_resources)

    assert "good" not in [i.metadata.name for i in offenders]
    assert "bad" in [i.metadata.name for i in offenders]


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
    assert check_endpoint_public_access(namespaced_resources)


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
    offenders = check_access_to_instance_profile(namespaced_resources)
    assert len(offenders) == 2


@patch("kubernetes.client.AppsV1Api.read_namespaced_daemon_set")
def test_check_aws_node_daemonset_service_account(mocked_client):
    test_data = (
        Path.cwd()
        / "tests"
        / "data"
        / "check_aws_node_daemonset_service_account"
        / "daemon_sets_api_response.json"
    )
    mocked_client.return_value = get_response(
        kubernetes.client.AppsV1Api,
        test_data,
        "V1DaemonSet",
    )

    namespaced_resources = NamespacedResources(
        "some_region", "some_context", "some_cluster", "some_ns"
    )
    assert check_aws_node_daemonset_service_account(namespaced_resources)


@pytest.mark.parametrize(
    "namespaced_resources",
    [("disable_service_account_token_mounts")],
    indirect=["namespaced_resources"],
)
def test_disable_service_account_token_mounts(namespaced_resources):
    offenders = disable_service_account_token_mounts(namespaced_resources)

    assert "good" not in [i.metadata.name for i in offenders]
    assert "bad" in [i.metadata.name for i in offenders]


@pytest.mark.parametrize(
    "namespaced_resources",
    [("disable_run_as_root_user")],
    indirect=["namespaced_resources"],
)
def test_disable_run_as_root_user(namespaced_resources):
    offenders = disable_run_as_root_user(namespaced_resources)

    assert "good" not in [i.metadata.name for i in offenders]
    assert "bad" in [i.metadata.name for i in offenders]


@pytest.mark.parametrize(
    "namespaced_resources",
    [("disable_anonymous_access_for_cluster_roles")],
    indirect=["namespaced_resources"],
)
def test_disable_anonymous_access_for_cluster_roles(namespaced_resources):
    offenders = disable_anonymous_access_for_cluster_roles(
        namespaced_resources
    )

    assert "good" not in [i.metadata.name for i in offenders]
    assert "bad" in [i.metadata.name for i in offenders]


@pytest.mark.parametrize(
    "namespaced_resources",
    [("disable_anonymous_access_for_roles")],
    indirect=["namespaced_resources"],
)
def test_disable_anonymous_access_for_roles(namespaced_resources):
    offenders = disable_anonymous_access_for_roles(namespaced_resources)

    assert "good" not in [i.metadata.name for i in offenders]
    assert "bad" in [i.metadata.name for i in offenders]


@pytest.mark.parametrize(
    "namespaced_resources",
    [("use_dedicated_service_accounts_for_each_daemon_set")],
    indirect=["namespaced_resources"],
)
def test_use_dedicated_service_accounts_for_each_daemon_set(
    namespaced_resources,
):
    offenders = use_dedicated_service_accounts_for_each_daemon_set(
        namespaced_resources
    )

    assert "shared-sa-1" in [i.metadata.name for i in offenders]
    assert "shared-sa-2" in [i.metadata.name for i in offenders]


@pytest.mark.parametrize(
    "namespaced_resources",
    [("use_dedicated_service_accounts_for_each_deployment")],
    indirect=["namespaced_resources"],
)
def test_use_dedicated_service_accounts_for_each_deployment(
    namespaced_resources,
):
    offenders = use_dedicated_service_accounts_for_each_deployment(
        namespaced_resources
    )

    assert "shared-sa-1" in [i.metadata.name for i in offenders]
    assert "shared-sa-2" in [i.metadata.name for i in offenders]


@pytest.mark.parametrize(
    "namespaced_resources",
    [("use_dedicated_service_accounts_for_each_stateful_set")],
    indirect=["namespaced_resources"],
)
def test_use_dedicated_service_accounts_for_each_stateful_set(
    namespaced_resources,
):
    offenders = use_dedicated_service_accounts_for_each_stateful_set(
        namespaced_resources
    )

    assert "shared-sa-1" in [i.metadata.name for i in offenders]
    assert "shared-sa-2" in [i.metadata.name for i in offenders]
