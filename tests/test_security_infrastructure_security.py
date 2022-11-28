import json
from pathlib import Path
from unittest.mock import patch

from hardeneks.cluster_wide.security.infrastructure_security import (
    deploy_workers_onto_private_subnets,
    make_sure_inspector_is_enabled,
)
from hardeneks.resources import Resources


def read_json(file_path):
    with open(file_path) as f:
        json_content = json.load(f)
    return json_content


def mocked_caller_identity():
    return {"Account": "foo"}


@patch("boto3.client")
def test_deploy_workers_onto_private_subnets(mocked_client):
    namespaced_resources = Resources(
        "some_region", "some_context", "some_cluster", "some_ns"
    )

    test_data = (
        Path.cwd()
        / "tests"
        / "data"
        / "deploy_workers_onto_private_subnets"
        / "instance_metadata.json"
    )

    mocked_client.return_value.describe_instances.return_value = read_json(
        test_data
    )
    offenders = deploy_workers_onto_private_subnets(namespaced_resources)
    instance_ids = [i["Instances"][0]["InstanceId"] for i in offenders]

    assert "i-063ca77fc509e2bf6" not in instance_ids
    assert "i-083cc9da5e18e2702" not in instance_ids
    assert "i-01c10da9688b958a0" in instance_ids
    assert "i-0f282d6ee7edb633f" in instance_ids


@patch("boto3.client")
def test_make_sure_inspector_is_enabled(mocked_client):
    namespaced_resources = Resources(
        "some_region", "some_context", "some_cluster", "some_ns"
    )

    test_data = (
        Path.cwd()
        / "tests"
        / "data"
        / "make_sure_inspector_is_enabled"
        / "inspector_status.json"
    )

    mocked_client.return_value.batch_get_account_status.return_value = (
        read_json(test_data)
    )
    mocked_client.return_value.get_caller_identity = mocked_caller_identity

    assert not make_sure_inspector_is_enabled(namespaced_resources)
