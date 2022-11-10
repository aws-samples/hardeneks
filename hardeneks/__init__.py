from pathlib import Path
import yaml

import kubernetes
from rich.console import Console
import typer

from .resources import NamespacedResources
from .harden import harden_namespace


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


def _get_namespaces(ignored_ns: list) -> list:
    v1 = kubernetes.client.CoreV1Api()
    namespaces = [i.metadata.name for i in v1.list_namespace().items]
    return list(set(namespaces) - set(ignored_ns))


@app.command()
def run_hardeneks(
    region: str = typer.Option(
        ..., help="AWS region of the cluster. Ex: us-east-1"
    ),
    context: str = typer.Option(
        ...,
        help="K8s context.",
    ),
    cluster: str = typer.Option(..., help="Cluster name."),
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

    console = Console()
    console.print(f"You are operating at {region}")
    console.print(f"You context is {context}")
    console.print(f"You are using {config} as your config file")
    console.print()

    kubernetes.config.load_kube_config(
        config_file=kube_config, context=context
    )

    with open(config, "r") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    if not namespace:
        namespaces = _get_namespaces(config["ignore-namespaces"])
    else:
        namespaces = [namespace]

    for ns in namespaces:
        console.print(f"Checking rules against namespace: {ns}", style="green")
        console.print()
        resources = NamespacedResources(region, context, cluster, ns)
        resources.set_resources()
        harden_namespace(resources, config["rules"])
