import pytest

from hardeneks.cluster_wide.security.encryption_secrets import (
    use_encryption_with_ebs,
    use_encryption_with_efs,
    use_efs_access_points,
)
from hardeneks.namespace_based.security.encryption_secrets import (
    disallow_secrets_from_env_vars,
)


@pytest.mark.parametrize(
    "resources",
    [("use_encryption_with_ebs")],
    indirect=["resources"],
)
def test_use_encryption_with_ebs(resources):
    offenders = use_encryption_with_ebs(resources)

    assert "good" not in [i.metadata.name for i in offenders]
    assert "bad" in [i.metadata.name for i in offenders]


@pytest.mark.parametrize(
    "resources",
    [("use_encryption_with_efs")],
    indirect=["resources"],
)
def test_use_encryption_with_efs(resources):
    offenders = use_encryption_with_efs(resources)

    assert "good" not in [i.metadata.name for i in offenders]
    assert "bad" in [i.metadata.name for i in offenders]


@pytest.mark.parametrize(
    "resources",
    [("use_efs_access_points")],
    indirect=["resources"],
)
def test_use_efs_access_points(resources):
    offenders = use_efs_access_points(resources)

    assert "good" not in [i.metadata.name for i in offenders]
    assert "bad" in [i.metadata.name for i in offenders]


@pytest.mark.parametrize(
    "namespaced_resources",
    [("disallow_secrets_from_env_vars")],
    indirect=["namespaced_resources"],
)
def test_disallow_secrets_from_env_vars(namespaced_resources):
    offenders = disallow_secrets_from_env_vars(namespaced_resources)

    assert "good" not in [i.metadata.name for i in offenders]
    assert "bad" in [i.metadata.name for i in offenders]
