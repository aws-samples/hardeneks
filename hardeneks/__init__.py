from pathlib import Path
import yaml

import kubernetes
from rich import print
import typer


app = typer.Typer()


def _config_callback(value: str):

    config = Path(value)

    if config.is_dir():
        raise typer.BadParameter(f"{config} is a directory")
    elif not config.exists():
        raise typer.BadParameter(f"{config} doesn't exist")

    with open(value, "r") as f:
        try:
            yaml.load(f, Loader=yaml.FullLoader)
        except yaml.YAMLError as exc:
            raise typer.BadParameter(exc)

    return value


@app.command()
def run_hardeneks(
    region: str = typer.Option(
        ..., help="AWS region of the cluster. Ex: us-east-1"
    ),
    context: str = typer.Option(
        ...,
        help="K8s context.",
    ),
    namespace: str = typer.Option(
        default=None,
        help="Specific namespace to harden. Default is all namespaces.",
    ),
    config: str = typer.Option(
        default=Path.cwd() / "config.yaml",
        callback=_config_callback,
        help="Path to a hardeneks config file.",
    ),
    kube_config: str = typer.Option(
        default=None, help="Path to the kube config file."
    ),
):
    print(f"You are operating at {region}")
    print(f"You context is {context}")
    print(f"You are using {config} as your config file")

    kubernetes.config.load_kube_config(
        config_file=kube_config, context=context
    )
