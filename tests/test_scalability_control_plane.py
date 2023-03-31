from hardeneks.resources import Resources
from unittest.mock import patch
from hardeneks import helpers

from hardeneks.cluster_wide.scalability.control_plane import (
    check_EKS_version,
    check_kubectl_compression,
)


class Version:
    def __init__(self, minor):
        self.major = 1
        self.minor = minor


@patch("kubernetes.client.VersionApi.get_code")
def test_check_EKS_version(mocked_client):
    namespaced_resources = Resources(
        "some_region", "some_context", "some_cluster", []
    )
    rule = check_EKS_version()
    mocked_client.return_value = Version("23+")
    rule.check(namespaced_resources)
    assert not rule.result.status
    mocked_client.return_value = Version("24+")
    rule.check(namespaced_resources)
    assert rule.result.status
    mocked_client.return_value = Version("24")
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
