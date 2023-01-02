from importlib import import_module

from hardeneks import console


def harden(resources, config, _type):
    config = config[_type]
    for pillar in config.keys():
        for section in config[pillar]:
            for rule in config[pillar][section]:
                module = import_module(f"hardeneks.{_type}.{pillar}.{section}")
                try:
                    func = getattr(module, rule)
                except AttributeError as exc:
                    console.print(f"[bold][red]{exc}")
                try:
                    func(resources)
                except Exception as exc:
                    console.print(f"[bold][red]{exc}")
