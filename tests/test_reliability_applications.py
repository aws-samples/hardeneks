import pytest

from hardeneks.namespace_based.reliability.applications import (
    avoid_running_singleton_pods,
    run_multiple_replicas,
    schedule_replicas_across_nodes,
    check_horizontal_pod_autoscaling_exists,
    check_liveness_probes,
    check_readiness_probes,
)

from hardeneks.cluster_wide.reliability.applications import (
    check_metrics_server_is_running,
    check_vertical_pod_autoscaler_exists,
)


@pytest.mark.parametrize(
    "namespaced_resources",
    [(("avoid_running_singleton_pods", ["pods"]))],
    indirect=["namespaced_resources"],
)
def test_avoid_running_singleton_pods(namespaced_resources):
    rule = avoid_running_singleton_pods()
    rule.check(namespaced_resources)

    assert all("good" not in r for r in rule.result.resources)
    assert all("bad" in r for r in rule.result.resources)


@pytest.mark.parametrize(
    "namespaced_resources",
    [(("run_multiple_replicas", ["deployments"]))],
    indirect=["namespaced_resources"],
)
def test_run_multiple_replicas(namespaced_resources):
    rule = run_multiple_replicas()

    rule.check(namespaced_resources)

    assert all("good" not in r for r in rule.result.resources)
    assert all("bad" in r for r in rule.result.resources)


@pytest.mark.parametrize(
    "namespaced_resources",
    [(("schedule_replicas_across_nodes", ["deployments"]))],
    indirect=["namespaced_resources"],
)
def test_schedule_replicas_across_nodes(namespaced_resources):
    rule = schedule_replicas_across_nodes()
    rule.check(namespaced_resources)

    assert all("good" not in r for r in rule.result.resources)
    assert all("bad" in r for r in rule.result.resources)


@pytest.mark.parametrize(
    "resources",
    [("check_metrics_server_is_running", ["services"])],
    indirect=["resources"],
)
def test_check_metrics_server_is_running(resources):
    rule = check_metrics_server_is_running()
    rule.check(resources)

    assert not rule.result.status


@pytest.mark.parametrize(
    "resources",
    [("check_vertical_pod_autoscaler_exists", ["deployments"])],
    indirect=["resources"],
)
def test_check_vertical_pod_autoscaler_exists(resources):
    rule = check_vertical_pod_autoscaler_exists()
    rule.check(resources)

    assert not rule.result.status


@pytest.mark.parametrize(
    "namespaced_resources",
    [(("check_horizontal_pod_autoscaling_exists", ["deployments", "hpas"]))],
    indirect=["namespaced_resources"],
)
def test_check_horizontal_pod_autoscaling_exists(namespaced_resources):
    rule = check_horizontal_pod_autoscaling_exists()

    rule.check(namespaced_resources)

    assert "good" not in rule.result.resources
    assert "bad" in rule.result.resources


@pytest.mark.parametrize(
    "namespaced_resources",
    [(("check_liveness_probes", ["pods"]))],
    indirect=["namespaced_resources"],
)
def test_check_liveness_probes(namespaced_resources):
    rule = check_liveness_probes()

    rule.check(namespaced_resources)

    assert all("good" not in r for r in rule.result.resources)
    assert all("bad" in r for r in rule.result.resources)


@pytest.mark.parametrize(
    "namespaced_resources",
    [(("check_readiness_probes", ["pods"]))],
    indirect=["namespaced_resources"],
)
def test_check_readiness_probes(namespaced_resources):
    rule = check_readiness_probes()

    rule.check(namespaced_resources)

    assert all("good" not in r for r in rule.result.resources)
    assert all("bad" in r for r in rule.result.resources)
