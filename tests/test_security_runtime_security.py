import pytest

from hardeneks.namespace_based.security.runtime_security import (
    disallow_linux_capabilities,
)


@pytest.mark.parametrize(
    "namespaced_resources",
    [("disallow_linux_capabilities")],
    indirect=["namespaced_resources"],
)
def test_disallow_linux_capabilities(namespaced_resources):
    rule = disallow_linux_capabilities()
    rule.check(namespaced_resources)
    assert "good" not in rule.result.resources
    assert "bad" in rule.result.resources
