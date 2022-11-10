import pytest

from hardeneks.security.iam import (
    restrict_wildcard_for_roles,
    restrict_wildcard_for_cluster_roles,
)


@pytest.mark.parametrize(
    "namespaced_resources",
    [("restrict_wildcard_for_roles")],
    indirect=["namespaced_resources"],
)
def test_restrict_wildcard_for_roles(namespaced_resources):
    offenders = restrict_wildcard_for_roles(namespaced_resources)

    assert "good" not in [i.metadata.name for i in offenders]
    assert "bad" in [i.metadata.name for i in offenders]


@pytest.mark.parametrize(
    "namespaced_resources",
    [("restrict_wildcard_for_cluster_roles")],
    indirect=["namespaced_resources"],
)
def test_restrict_wildcard_for_cluster_roles(namespaced_resources):
    offenders = restrict_wildcard_for_cluster_roles(namespaced_resources)

    assert "good" not in [i.metadata.name for i in offenders]
    assert "bad" in [i.metadata.name for i in offenders]
