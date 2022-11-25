from pathlib import Path
from unittest.mock import patch

import kubernetes
import pytest

from hardeneks.namespace_based.security.pod_security import (
    disallow_container_socket_mount,
    disallow_host_path_or_make_it_read_only,
    set_requests_limits_for_containers,
    disallow_privilege_escalation,
    check_read_only_root_file_system,
)
from hardeneks.cluster_wide.security.pod_security import (
    ensure_namespace_psa_exist,
)
from hardeneks.resources import Resources

from .conftest import get_response


@pytest.mark.parametrize(
    "namespaced_resources",
    [("disallow_container_socket_mount")],
    indirect=["namespaced_resources"],
)
def test_disallow_container_socket_mount(namespaced_resources):
    offenders = disallow_container_socket_mount(namespaced_resources)

    assert "bad" in [i.metadata.name for i in offenders]


@pytest.mark.parametrize(
    "namespaced_resources",
    [("disallow_host_path_or_make_it_read_only")],
    indirect=["namespaced_resources"],
)
def test_disallow_host_path_or_make_it_read_only(namespaced_resources):
    offenders = disallow_host_path_or_make_it_read_only(namespaced_resources)

    assert "bad" in [i.metadata.name for i in offenders]


@pytest.mark.parametrize(
    "namespaced_resources",
    [("set_requests_limits_for_containers")],
    indirect=["namespaced_resources"],
)
def test_set_requests_limits_for_containers(namespaced_resources):
    offenders = set_requests_limits_for_containers(namespaced_resources)

    assert "good" not in [i.metadata.name for i in offenders]
    assert "bad" in [i.metadata.name for i in offenders]


@pytest.mark.parametrize(
    "namespaced_resources",
    [("disallow_privilege_escalation")],
    indirect=["namespaced_resources"],
)
def test_disallow_privilege_escalation(namespaced_resources):
    offenders = disallow_privilege_escalation(namespaced_resources)

    assert "good" not in [i.metadata.name for i in offenders]
    assert "bad" in [i.metadata.name for i in offenders]


@pytest.mark.parametrize(
    "namespaced_resources",
    [("check_read_only_root_file_system")],
    indirect=["namespaced_resources"],
)
def test_check_read_only_root_file_system(namespaced_resources):
    offenders = check_read_only_root_file_system(namespaced_resources)

    assert "good" not in [i.metadata.name for i in offenders]
    assert "bad" in [i.metadata.name for i in offenders]


@patch("kubernetes.client.CoreV1Api.list_namespace")
def test_ensure_namespace_psa_exist(mocked_client):

    test_data = (
        Path.cwd()
        / "tests"
        / "data"
        / "ensure_namespace_psa_exist"
        / "cluster"
        / "namespaces_api_response.json"
    )
    mocked_client.return_value = get_response(
        kubernetes.client.CoreV1Api,
        test_data,
        "V1NamespaceList",
    )
    resources = Resources(
        "some_region",
        "some_context",
        "some_cluster",
        ["kube-node-lease", "kube-public", "kube-system", "kube-apiserver"],
    )
    offenders = ensure_namespace_psa_exist(resources)

    assert offenders == ["bad", "default", "test-namespace"]
