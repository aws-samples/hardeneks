from hardeneks.resources import Resources
from unittest.mock import patch
from hardeneks import helpers

from hardeneks.cluster_wide.scalability.control_plane import (
    check_EKS_version,
    check_kubectl_compression
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
    mocked_client.return_value = Version("23+")
    assert not check_EKS_version(namespaced_resources)
    mocked_client.return_value = Version("24+")
    assert check_EKS_version(namespaced_resources)
    mocked_client.return_value = Version("24")
    assert check_EKS_version(namespaced_resources)

@patch(helpers.__name__ + ".get_kube_config")
def test_check_kubectl_compression(mocked_helpers):
    namespaced_resources = Resources(
        "some_region", "some_context", "foobarcluster", []
    )
    mocked_helpers.return_value = {'clusters': [{'cluster': {'server': 'testtest', 'disable-compression': True}, 'name': 'foobarcluster'}]}
    assert check_kubectl_compression(namespaced_resources)
    mocked_helpers.return_value = {'clusters': [{'cluster': {'server': 'testtest', 'disable-compression': True}, 'name': 'foobarcluster'}, {'cluster': {'server': 'testtest', 'disable-compression': False}, 'name': 'foobarcluster2'}]}
    assert check_kubectl_compression(namespaced_resources)
    mocked_helpers.return_value = {'clusters': [{'cluster': {'server': 'testtest', 'disable-compression': False}, 'name': 'foobarcluster'}, {'cluster': {'server': 'testtest', 'disable-compression': False}, 'name': 'foobarcluster4'}]}
    assert not check_kubectl_compression(namespaced_resources)
    mocked_helpers.return_value = {'clusters': [{'cluster': {'test': 'user'}, 'name': 'foobarcluster7'}]}
    assert not check_kubectl_compression(namespaced_resources)
    mocked_helpers.return_value = {'clusters': [{}]}
    assert not check_kubectl_compression(namespaced_resources)
    mocked_helpers.return_value = {}
    assert not check_kubectl_compression(namespaced_resources)