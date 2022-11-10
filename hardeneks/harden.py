from importlib import import_module

from .resources import NamespacedResources


def harden_namespace(resources: NamespacedResources, config: list):
    try:
        for pillar in config.keys():
            for section in config[pillar]:
                for rule in config[pillar][section]:
                    module = import_module(f"hardeneks.{pillar}.{section}")
                    func = getattr(module, rule)
                    func(resources)
    except TypeError:
        pass
