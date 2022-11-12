import pytest

from hardeneks.security.multi_tenancy import ensure_namespace_quotas_exist


@pytest.mark.parametrize(
    "namespaced_resources",
    [("ensure_namespace_quotas_exist")],
    indirect=["namespaced_resources"],
)
def test_ensure_namespace_quotas_exist(namespaced_resources):
    offenders = ensure_namespace_quotas_exist(namespaced_resources)

    assert "good" not in offenders
    assert "bad" in offenders
