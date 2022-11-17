import json
from pathlib import Path
from unittest.mock import patch

from hardeneks.resources import NamespacedResources
from hardeneks.cluster_wide.security.detective_controls import (
    check_logs_are_enabled,
)


def read_json(file_path):
    with open(file_path) as f:
        json_content = json.load(f)
    return json_content


@patch("boto3.client")
def test_check_logs_are_enabled(mocked_client):
    namespaced_resources = NamespacedResources(
        "some_region", "some_context", "some_cluster", "some_ns"
    )
    test_data = (
        Path.cwd()
        / "tests"
        / "data"
        / "check_logs_are_enabled"
        / "cluster_metadata.json"
    )

    mocked_client.return_value.describe_cluster.return_value = read_json(
        test_data
    )

    assert not check_logs_are_enabled(namespaced_resources)
