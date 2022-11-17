from importlib import import_module


def harden(resources, config, _type):
    config = config[_type]
    for pillar in config.keys():
        for section in config[pillar]:
            for rule in config[pillar][section]:
                module = import_module(f"hardeneks.{_type}.{pillar}.{section}")
                func = getattr(module, rule)
                func(resources)
