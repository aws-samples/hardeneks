from hardeneks.resources import Resources
from unittest.mock import patch

from hardeneks.cluster_wide.scalability.control_plane import check_EKS_version


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
