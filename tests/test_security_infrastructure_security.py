import json
from pathlib import Path
from unittest.mock import patch

from hardeneks.cluster_wide.security.infrastructure_security import (
    deploy_workers_onto_private_subnets,
)
from hardeneks.resources import Resources


def read_json(file_path):
    with open(file_path) as f:
        json_content = json.load(f)
    return json_content


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
