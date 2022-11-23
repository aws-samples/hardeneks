from pathlib import Path
from unittest.mock import patch

import kubernetes
import pytest

from hardeneks.resources import Resources
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
from .conftest import get_response


@pytest.mark.parametrize(
    "namespaced_resources",
    [("avoid_running_singleton_pods")],
    indirect=["namespaced_resources"],
)
def test_avoid_running_singleton_pods(namespaced_resources):
    offenders = avoid_running_singleton_pods(namespaced_resources)

    assert "good" not in [i.metadata.name for i in offenders]
    assert "bad" in [i.metadata.name for i in offenders]


@pytest.mark.parametrize(
    "namespaced_resources",
    [("run_multiple_replicas")],
    indirect=["namespaced_resources"],
)
def test_run_multiple_replicas(namespaced_resources):
    offenders = run_multiple_replicas(namespaced_resources)

    assert "good" not in [i.metadata.name for i in offenders]
    assert "bad" in [i.metadata.name for i in offenders]


@pytest.mark.parametrize(
    "namespaced_resources",
    [("schedule_replicas_across_nodes")],
    indirect=["namespaced_resources"],
)
def test_schedule_replicas_across_nodes(namespaced_resources):
    offenders = schedule_replicas_across_nodes(namespaced_resources)

    assert "good" not in [i.metadata.name for i in offenders]
    assert "bad" in [i.metadata.name for i in offenders]


@patch("kubernetes.client.CoreV1Api.list_service_for_all_namespaces")
def test_check_metrics_server_is_running(mocked_client):
    test_data = (
        Path.cwd()
        / "tests"
        / "data"
        / "check_metrics_server_is_running"
        / "cluster"
        / "services_api_response.json"
    )
    mocked_client.return_value = get_response(
        kubernetes.client.CoreV1Api,
        test_data,
        "V1ServiceList",
    )
    namespaced_resources = Resources(
        "some_region", "some_context", "some_cluster", []
    )

    assert not check_metrics_server_is_running(namespaced_resources)


@patch("kubernetes.client.AppsV1Api.list_deployment_for_all_namespaces")
def test_check_vertical_pod_autoscaler_exists(mocked_client):
    test_data = (
        Path.cwd()
        / "tests"
        / "data"
        / "check_vertical_pod_autoscaler_exists"
        / "cluster"
        / "deployments_api_response.json"
    )

    mocked_client.return_value = get_response(
        kubernetes.client.AppsV1Api,
        test_data,
        "V1DeploymentList",
    )

    namespaced_resources = Resources(
        "some_region", "some_context", "some_cluster", []
    )

    assert not check_vertical_pod_autoscaler_exists(namespaced_resources)


@pytest.mark.parametrize(
    "namespaced_resources",
    [("check_horizontal_pod_autoscaling_exists")],
    indirect=["namespaced_resources"],
)
def test_check_horizontal_pod_autoscaling_exists(namespaced_resources):
    offenders = check_horizontal_pod_autoscaling_exists(namespaced_resources)

    assert "good" not in [i.metadata.name for i in offenders]
    assert "bad" in [i.metadata.name for i in offenders]


@pytest.mark.parametrize(
    "namespaced_resources",
    [("check_liveness_probes")],
    indirect=["namespaced_resources"],
)
def test_check_liveness_probes(namespaced_resources):
    offenders = check_liveness_probes(namespaced_resources)

    assert "good" not in [i.metadata.name for i in offenders]
    assert "bad" in [i.metadata.name for i in offenders]


@pytest.mark.parametrize(
    "namespaced_resources",
    [("check_readiness_probes")],
    indirect=["namespaced_resources"],
)
def test_check_readiness_probes(namespaced_resources):
    offenders = check_readiness_probes(namespaced_resources)

    assert "good" not in [i.metadata.name for i in offenders]
    assert "bad" in [i.metadata.name for i in offenders]
