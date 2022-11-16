import pytest

from hardeneks.cluster_wide.encryption_secrets import (
    use_encryption_with_ebs,
    use_encryption_with_efs,
    use_efs_access_points,
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
