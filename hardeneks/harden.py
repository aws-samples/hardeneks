from importlib import import_module


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
                    print(f"[bold][red]{exc}")
                try:
                    rule = cls()
                    rule.check(resources)
                    results.append(rule)
                except Exception as exc:
                    print(f"[bold][red]{exc}")

    return results
