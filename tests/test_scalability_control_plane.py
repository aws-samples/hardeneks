import pytest
from hardeneks.resources import Resources
from hardeneks.resources import Map
from unittest.mock import patch
 
from hardeneks.cluster_wide.scalability.control_plane import (
    check_EKS_version
)

@patch("hardeneks.cluster_wide.scalability.control_plane._get_version")
def test_check_EKS_version(mocked_client):
    namespaced_resources = Resources(
        "some_region", "some_context", "some_cluster", []
    )
    mocked_client.return_value = Map({'major': '1', 'minor': "23+"})
    good = check_EKS_version(namespaced_resources)
    assert good == False, "Value should be False"
    mocked_client.return_value = Map({'major': '1', 'minor': "24+"})
    good = check_EKS_version(namespaced_resources)
    assert good == True, "Value should be True"
    mocked_client.return_value = Map({'major': '1', 'minor': "24"})
    good = check_EKS_version(namespaced_resources)
    assert good == True, "Value should be True and Handle without +"