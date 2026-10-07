from hardeneks.resources import Resources
from unittest.mock import patch
from hardeneks import helpers

from hardeneks.cluster_wide.scalability.control_plane import (
    check_eks_version,
    check_kubectl_compression,
)


class Version:
    def __init__(self, minor):
        self.major = 1
        self.minor = minor


@patch("boto3.client")
def test_check_eks_version(mocked_boto_client):
    namespaced_resources = Resources(
        "some_region", "some_context", "some_cluster", []
    )
    rule = check_eks_version()

    # Mock EKS client
    mocked_eks = mocked_boto_client.return_value

    # Test: Cluster in extended support (should fail)
    mocked_eks.describe_cluster.return_value = {"cluster": {"version": "1.29"}}
    mocked_eks.describe_cluster_versions.return_value = {
        "clusterVersions": [
            {"clusterVersion": "1.32", "versionStatus": "STANDARD_SUPPORT"},
            {"clusterVersion": "1.31", "versionStatus": "STANDARD_SUPPORT"},
            {"clusterVersion": "1.30", "versionStatus": "EXTENDED_SUPPORT"},
            {"clusterVersion": "1.29", "versionStatus": "EXTENDED_SUPPORT"},
        ]
    }
    rule.check(namespaced_resources)
    assert not rule.result.status

    # Test: Cluster in standard support (should pass)
    mocked_eks.describe_cluster.return_value = {"cluster": {"version": "1.32"}}
    rule.check(namespaced_resources)
    assert rule.result.status


@patch(helpers.__name__ + ".get_kube_config")
def test_check_kubectl_compression(mocked_helpers):
    namespaced_resources = Resources(
        "some_region", "some_context", "foobarcluster", []
    )
    rule = check_kubectl_compression()

    mocked_helpers.return_value = {
        "clusters": [
            {
                "cluster": {"server": "testtest", "disable-compression": True},
                "name": "foobarcluster",
            }
        ]
    }
    rule.check(namespaced_resources)
    assert rule.result.status

    mocked_helpers.return_value = {
        "clusters": [
            {
                "cluster": {"server": "testtest", "disable-compression": True},
                "name": "foobarcluster",
            },
            {
                "cluster": {
                    "server": "testtest",
                    "disable-compression": False,
                },
                "name": "foobarcluster2",
            },
        ]
    }
    rule.check(namespaced_resources)
    assert rule.result.status

    mocked_helpers.return_value = {
        "clusters": [
            {
                "cluster": {
                    "server": "testtest",
                    "disable-compression": False,
                },
                "name": "foobarcluster",
            },
            {
                "cluster": {
                    "server": "testtest",
                    "disable-compression": False,
                },
                "name": "foobarcluster4",
            },
        ]
    }
    rule.check(namespaced_resources)
    assert not rule.result.status

    mocked_helpers.return_value = {
        "clusters": [{"cluster": {"test": "user"}, "name": "foobarcluster7"}]
    }
    rule.check(namespaced_resources)
    assert not rule.result.status

    mocked_helpers.return_value = {"clusters": [{}]}
    rule.check(namespaced_resources)
    assert not rule.result.status

    mocked_helpers.return_value = {}
    rule.check(namespaced_resources)
    assert not rule.result.status
