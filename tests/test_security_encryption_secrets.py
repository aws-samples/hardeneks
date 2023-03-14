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
    rule = use_encryption_with_ebs()
    rule.check(resources)

    assert "good" not in rule.result.resources
    assert "bad" in rule.result.resources


@pytest.mark.parametrize(
    "resources",
    [("use_encryption_with_efs")],
    indirect=["resources"],
)
def test_use_encryption_with_efs(resources):
    rule = use_encryption_with_efs()
    rule.check(resources)

    assert "good" not in rule.result.resources
    assert "bad" in rule.result.resources


@pytest.mark.parametrize(
    "resources",
    [("use_efs_access_points")],
    indirect=["resources"],
)
def test_use_efs_access_points(resources):
    rule = use_efs_access_points()
    rule.check(resources)

    assert "good" not in rule.result.resources
    assert "bad" in rule.result.resources


@pytest.mark.parametrize(
    "namespaced_resources",
    [("disallow_secrets_from_env_vars")],
    indirect=["namespaced_resources"],
)
def test_disallow_secrets_from_env_vars(namespaced_resources):
    offenders = disallow_secrets_from_env_vars(namespaced_resources)

    assert "good" not in [i.metadata.name for i in offenders]
    assert "bad" in [i.metadata.name for i in offenders]
