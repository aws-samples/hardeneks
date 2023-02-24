from hardeneks.resources import Resources
from unittest.mock import patch

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

@patch("kubernetes.config.list_kube_config_contexts")
def test_check_kubectl_compression(mocked_client):
    namespaced_resources = Resources(
        "some_region", "some_context", "some_cluster", []
    )
    mocked_client.return_value = None, {'context': {'cluster': 'test', 'user': 'foo', 'disable-compression': True}, 'name': 'foobarcluster'}
    assert check_kubectl_compression(namespaced_resources)
    mocked_client.return_value = None, {'context': {'cluster': 'test', 'user': 'foo'}, 'name': 'foobarcluster'}
    assert not check_kubectl_compression(namespaced_resources)
    mocked_client.return_value = None, {'name': 'foobarcluster'}
    assert not check_kubectl_compression(namespaced_resources)
    mocked_client.return_value = None, {'context': {'cluster': 'test', 'user': 'foo', 'disable-compression': False}, 'name': 'foobarcluster'}
    assert not check_kubectl_compression(namespaced_resources)