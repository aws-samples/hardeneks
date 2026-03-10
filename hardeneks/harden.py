from importlib import import_module
from rich.console import Console

console = Console()


def harden(resources, config, _type):
    config = config[_type]
    results = []
    for pillar in config.keys():
        for section in config[pillar]:
            for rule in config[pillar][section]:
                module = import_module(f"hardeneks.{_type}.{pillar}.{section}")
                try:
                    cls = getattr(module, rule)
                except AttributeError as exc:
                    console.print(f"[bold red]Error loading rule '{rule}': {exc}")
                    continue
                try:
                    rule_instance = cls()
                    rule_instance.check(resources)
                    results.append(rule_instance)
                except Exception as exc:
                    console.print(f"[bold red]Error in rule '{rule}': {exc}")

    return results
