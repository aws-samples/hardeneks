import json
import kubernetes
from pathlib import Path
from unittest.mock import patch

import pytest

from hardeneks.security.network_security import (
    use_encryption_with_aws_load_balancers,
)
from hardeneks.cluster_wide.network_security import (
    check_vpc_flow_logs,
    check_awspca_exists,
    check_default_deny_policy_exists,
)
from hardeneks.resources import Resources
from .conftest import get_response


def read_json(file_path):
    with open(file_path) as f:
        json_content = json.load(f)
    return json_content


@pytest.mark.parametrize(
    "namespaced_resources",
    [("use_encryption_with_aws_load_balancers")],
    indirect=["namespaced_resources"],
)
def test_use_encryption_with_aws_load_balancers(namespaced_resources):
    offenders = use_encryption_with_aws_load_balancers(namespaced_resources)

    assert "good" not in [i.metadata.name for i in offenders]
    assert "bad" in [i.metadata.name for i in offenders]


@patch("boto3.client")
def test_check_vpc_flow_logs(mocked_client):
    resources = Resources("some_region", "some_context", "some_cluster", [])
    test_data = (
        Path.cwd()
        / "tests"
        / "data"
        / "check_vpc_flow_logs"
        / "cluster_metadata.json"
    )

    mocked_client.return_value.describe_cluster.return_value = read_json(
        test_data
    )

    mocked_client.return_value.describe_flow_logs.return_value = {
        "FlowLogs": []
    }

    assert not check_vpc_flow_logs(resources)


@pytest.mark.parametrize(
    "resources",
    [("check_default_deny_policy_exists")],
    indirect=["resources"],
)
def test_check_default_deny_policy_exists(resources):
    offenders = check_default_deny_policy_exists(resources)
    assert ["good", "bad", "default"] == offenders


@patch("kubernetes.client.CoreV1Api.list_service_for_all_namespaces")
def test_check_awspca_exists(mocked_client):
    test_data = (
        Path.cwd()
        / "tests"
        / "data"
        / "check_awspca_exists"
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

    assert not check_awspca_exists(namespaced_resources)
