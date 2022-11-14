from importlib import import_module

from .resources import NamespacedResources, Resources


def harden_namespace(resources: NamespacedResources, config: dict):
    for pillar in config.keys():
        for section in config[pillar]:
            for rule in config[pillar][section]:
                module = import_module(f"hardeneks.{pillar}.{section}")
                func = getattr(module, rule)
                func(resources)


def harden_cluster(resources: Resources, config: dict):
    for pillar in config.keys():
        for rule in config[pillar]:
            module = import_module(f"hardeneks.cluster_wide.{pillar}")
            func = getattr(module, rule)
            func(resources)
