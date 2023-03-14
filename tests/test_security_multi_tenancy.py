import pytest

from hardeneks.cluster_wide.security.multi_tenancy import (
    ensure_namespace_quotas_exist,
)


@pytest.mark.parametrize(
    "resources",
    [("ensure_namespace_quotas_exist")],
    indirect=["resources"],
)
def test_ensure_namespace_quotas_exist(resources):
    rule = ensure_namespace_quotas_exist()
    rule.check(resources)

    assert "good" not in rule.result.resources
    assert "bad" in rule.result.resources
