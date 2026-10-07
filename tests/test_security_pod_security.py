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


@pytest.mark.parametrize(
    "namespaced_resources",
    [(("disallow_container_socket_mount", ["pods"]))],
    indirect=["namespaced_resources"],
)
def test_disallow_container_socket_mount(namespaced_resources):
    rule = disallow_container_socket_mount()
    rule.check(namespaced_resources)

    assert all("good" not in r for r in rule.result.resources)
    assert all("bad" in r for r in rule.result.resources)


@pytest.mark.parametrize(
    "namespaced_resources",
    [(("disallow_host_path_or_make_it_read_only", ["pods"]))],
    indirect=["namespaced_resources"],
)
def test_disallow_host_path_or_make_it_read_only(namespaced_resources):
    rule = disallow_host_path_or_make_it_read_only()
    rule.check(namespaced_resources)

    assert len(rule.result.resources) == 1
    assert all("good" not in r for r in rule.result.resources)
    assert all("bad" in r for r in rule.result.resources)


@pytest.mark.parametrize(
    "namespaced_resources",
    [(("set_requests_limits_for_containers", ["pods"]))],
    indirect=["namespaced_resources"],
)
def test_set_requests_limits_for_containers(namespaced_resources):
    rule = set_requests_limits_for_containers()
    rule.check(namespaced_resources)

    assert len(rule.result.resources) == 2
    assert all("good" not in r for r in rule.result.resources)
    assert all("bad" in r for r in rule.result.resources)


@pytest.mark.parametrize(
    "namespaced_resources",
    [(("disallow_privilege_escalation", ["pods"]))],
    indirect=["namespaced_resources"],
)
def test_disallow_privilege_escalation(namespaced_resources):
    rule = disallow_privilege_escalation()
    rule.check(namespaced_resources)

    assert all("good" not in r for r in rule.result.resources)
    assert all("bad" in r for r in rule.result.resources)


@pytest.mark.parametrize(
    "namespaced_resources",
    [(("check_read_only_root_file_system", ["pods"]))],
    indirect=["namespaced_resources"],
)
def test_check_read_only_root_file_system(namespaced_resources):
    rule = check_read_only_root_file_system()
    rule.check(namespaced_resources)

    assert len(rule.result.resources) == 2
    assert all("good" not in r for r in rule.result.resources)


@pytest.mark.parametrize(
    "resources",
    [("ensure_namespace_psa_exist", ["namespace_list"])],
    indirect=["resources"],
)
def test_ensure_namespace_psa_exist(resources):
    resources.namespaces = ["bad", "good"]
    rule = ensure_namespace_psa_exist()
    rule.check(resources)

    assert rule.result.resources == ["bad"]
