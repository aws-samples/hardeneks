from pathlib import Path
from pkg_resources import resource_filename
import yaml

from botocore.exceptions import EndpointConnectionError
import boto3
import kubernetes
from rich.console import Console
import typer

from .resources import (
    NamespacedResources,
    Resources,
)
from .harden import harden


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


def _get_current_context(context):
    if context:
        return context
    _, active_context = kubernetes.config.list_kube_config_contexts()
    return active_context["name"]


def _get_namespaces(ignored_ns: list) -> list:
    v1 = kubernetes.client.CoreV1Api()
    namespaces = [i.metadata.name for i in v1.list_namespace().items]
    return list(set(namespaces) - set(ignored_ns))


def _get_cluster_name(context, region):
    try:
        client = boto3.client("eks", region_name=region)
        for name in client.list_clusters()["clusters"]:
            if name in context:
                return name
    except EndpointConnectionError:
        raise ValueError(f"{region} seems like a bad region name")


def _get_region():
    return boto3.session.Session().region_name


@app.command()
def run_hardeneks(
    region: str = typer.Option(
        default=None, help="AWS region of the cluster. Ex: us-east-1"
    ),
    context: str = typer.Option(
        default=None,
        help="K8s context.",
    ),
    cluster: str = typer.Option(default=None, help="Cluster name."),
    namespace: str = typer.Option(
        default=None,
        help="Specific namespace to harden. Default is all namespaces.",
    ),
    config: str = typer.Option(
        default=resource_filename(__name__, "config.yaml"),
        callback=_config_callback,
        help="Path to a hardeneks config file.",
    ),
):
    """
    Main entry point to hardeneks.

    Args:
        region (str): AWS region of the cluster. Ex: us-east-1
        context (str): K8s context
        cluster (str): Cluster name
        namespace (str): Specific namespace to be checked
        config (str): Path to hardeneks config file

    Returns:
        None

    """

    kubernetes.config.load_kube_config(context=context)
    context = _get_current_context(context)
    if not cluster:
        cluster = _get_cluster_name(context, region)

    if not region:
        region = _get_region()

    console = Console()
    console.rule("[b]HARDENEKS", characters="*  ")
    console.print(f"You are operating at {region}")
    console.print(f"You context is {context}")
    console.print(f"Your cluster name is {cluster}")
    console.print(f"You are using {config} as your config file")
    console.print()

    with open(config, "r") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    if not namespace:
        namespaces = _get_namespaces(config["ignore-namespaces"])
    else:
        namespaces = [namespace]

    rules = config["rules"]

    console.rule("[b]Checking cluster wide rules", characters="- ")
    print()

    resources = Resources(region, context, cluster, namespaces)
    resources.set_resources()
    harden(resources, rules, "cluster_wide")

    for ns in namespaces:
        console.rule(
            f"[b]Checking rules against namespace: {ns}", characters=" -"
        )
        console.print()
        resources = NamespacedResources(region, context, cluster, ns)
        resources.set_resources()
        harden(resources, rules, "namespace_based")
        console.print()
