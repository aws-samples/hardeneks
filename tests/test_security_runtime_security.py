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
    offenders = disallow_linux_capabilities(namespaced_resources)

    assert "good" not in [i.metadata.name for i in offenders]
    assert "bad" in [i.metadata.name for i in offenders]
