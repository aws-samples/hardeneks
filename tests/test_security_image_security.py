import json
from pathlib import Path
from unittest.mock import patch

from hardeneks.resources import Resources
from hardeneks.cluster_wide.security.image_security import (
    use_immutable_tags_with_ecr,
)


def read_json(file_path):
    with open(file_path) as f:
        json_content = json.load(f)
    return json_content


@patch("boto3.client")
def test_use_immutable_tags_with_ecr(mocked_client):
    namespaced_resources = Resources(
        "some_region", "some_context", "some_cluster", "some_ns"
    )

    test_data = (
        Path.cwd()
        / "tests"
        / "data"
        / "use_immutable_tags_with_ecr"
        / "repositories.json"
    )

    mocked_client.return_value.describe_repositories.return_value = read_json(
        test_data
    )
    offenders = use_immutable_tags_with_ecr(namespaced_resources)
    offender_names = [i["repositoryName"] for i in offenders]
    assert (
        "rolling-deployment-service-ecrrepo714fb1b2-xbs3hua1h3ud"
        in offender_names
    )
    assert (
        "rolling-deployment-service-ecrrepo714fb1b2-nyrkgiafcyyx"
        not in offender_names
    )
