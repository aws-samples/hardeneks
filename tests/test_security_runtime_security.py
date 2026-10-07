import pytest

from hardeneks.namespace_based.security.runtime_security import (
    disallow_linux_capabilities,
)


@pytest.mark.parametrize(
    "namespaced_resources",
    [(("disallow_linux_capabilities", ["pods"]))],
    indirect=["namespaced_resources"],
)
def test_disallow_linux_capabilities(namespaced_resources):
    rule = disallow_linux_capabilities()
    rule.check(namespaced_resources)

    assert all("good" not in r for r in rule.result.resources)
    assert all("bad" in r for r in rule.result.resources)
