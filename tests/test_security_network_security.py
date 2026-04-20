import json
import kubernetes
from pathlib import Path
from unittest.mock import patch

import pytest

from hardeneks.namespace_based.security.network_security import (
    use_encryption_with_aws_load_balancers,
)
from hardeneks.cluster_wide.security.network_security import (
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
    [(("use_encryption_with_aws_load_balancers", ["services"]))],
    indirect=["namespaced_resources"],
)
def test_use_encryption_with_aws_load_balancers(namespaced_resources):
    rule = use_encryption_with_aws_load_balancers()
    rule.check(namespaced_resources)

    assert all("good" not in r for r in rule.result.resources)
    assert all("bad" in r for r in rule.result.resources)


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
    rule = check_vpc_flow_logs()
    rule.check(resources)

    assert not rule.result.status


@pytest.mark.parametrize(
    "resources",
    [(("check_default_deny_policy_exists", ["network_policies"]))],
    indirect=["resources"],
)
def test_check_default_deny_policy_exists(resources):
    rule = check_default_deny_policy_exists()
    rule.check(resources)
    assert sorted(["bad"]) == sorted(rule.result.resources)


@pytest.mark.parametrize(
    "resources",
    [(("check_awspca_exists", ["services"]))],
    indirect=["resources"],
)
def test_check_awspca_exists(resources):
    rule = check_awspca_exists()
    rule.check(resources)

    assert not rule.result.status
