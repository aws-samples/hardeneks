import os
from pathlib import Path
from pkg_resources import resource_filename
import tempfile
import yaml
import json
from collections import defaultdict
import csv

from botocore.exceptions import EndpointConnectionError
import boto3
import kubernetes
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
import typer

from .resources import (
    NamespacedResources,
    Resources,
)
from .harden import harden
from hardeneks import helpers

import datetime
import hashlib

app = typer.Typer()
console = Console(record=True)


def _config_callback(value: str):

    config = Path(value)

    if config.is_dir():
        raise typer.BadParameter(f"{config} is a directory")
    elif not config.exists():
        raise typer.BadParameter(f"{config} doesn't exist")

    with open(value, "r") as f:
        try:
            yaml.safe_load(f)
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


def _add_tls_verify():
    kubeconfig = helpers.get_kube_config()
    tmp_config = tempfile.NamedTemporaryFile().name

    for cluster in kubeconfig["clusters"]:
        cluster["cluster"]["insecure-skip-tls-verify"] = True
    with open(tmp_config, "w") as fd:
        yaml.dump(kubeconfig, fd, default_flow_style=False)

    kubernetes.config.load_kube_config(tmp_config)
    os.remove(tmp_config)


def _export_json(rules: list, json_path=str):
    def ndd():
        return defaultdict(ndd)

    json_blob = ndd()

    for rule in rules:
        result = {
            "status": rule.result.status,
            "resources": rule.result.resources,
            "resource_type": rule.result.resource_type,
            "namespace": rule.result.namespace,
            "resolution": rule.url,
        }
        json_blob[rule._type][rule.pillar][rule.section][rule.message] = result
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(json_blob, f, ensure_ascii=False, indent=4)

def _export_csv(rules: list, csv_path=str):
    csv_data = []

    for rule in rules:
        csv_row = {
           "Type": rule._type,
            "Pillar": rule.pillar,
            "Section": rule.section,
            "Message": rule.message,
            "Status": rule.result.status,
            "Resources": ', '.join(rule.result.resources) if rule.result.resources else '',
            "Resource Type": rule.result.resource_type,
            "Namespace": rule.result.namespace,
            "Resolution": rule.url,
        }
        csv_data.append(csv_row)

    with open(csv_path, "w", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=csv_data[0].keys())
        writer.writeheader()
        writer.writerows(csv_data)

def _export_security_hub(rules: list,region,context):
    """
    Export failed checks to AWS Security Hub as custom findings
    """
    try:
        security_hub = boto3.client('securityhub', region_name=region)
        account_id = boto3.client('sts').get_caller_identity()['Account']
        
        findings = []
        current_time = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
        
        for rule in rules:
            if not rule.result.status:  # Only process failed checks
                # Process each failed resource as a separate finding
                resources = rule.result.resources if rule.result.resources else ['NoSpecificResource']
                
                for resource in resources:
                    finding = {
                        'SchemaVersion': '2018-10-08',
                        'Id': f"hardeneks/{rule.pillar}/{rule.section}/{hashlib.md5(resource.encode()).hexdigest()}",
                        'ProductArn': f"arn:aws:securityhub:{region}:{account_id}:product/{account_id}/default",
                        'GeneratorId': f"hardeneks/{rule.pillar}/{rule.section}",
                        'AwsAccountId': account_id,
                        'Types': [
                            'Software and Configuration Checks/AWS Security Best Practices'
                        ],
                        'CreatedAt': current_time,
                        'UpdatedAt': current_time,
                        'Severity': {
                            'Label': 'HIGH'
                        },
                        'Title': rule.message,
                        'Description': f"HardenEKS check failed: {rule.message}",
                        'Resources': [{
                            'Type': f'EKS {rule.result.resource_type}',
                            'Id': context,
                            'Partition': 'aws',
                            'Region': region
                        }],
                        'Compliance': {
                            'Status': 'FAILED'
                        },
                        'RecordState': 'ACTIVE',
                        'Workflow': {
                            'Status': 'NEW'
                        },
                        'ProductFields': {
                            'Provider': 'HardenEKS',
                            'Pillar': rule.pillar,
                            'Section': rule.section
                        }
                    }
                    
                    # Add namespace information if available
                    if rule.result.namespace:
                        finding['ProductFields']['Namespace'] = rule.result.namespace
                        
                    # Add remediation URL if available
                    if rule.url:
                        finding['Remediation'] = {
                            'Recommendation': {
                                'Text': 'For remediation steps, see the Amazon EKS Best Practices documentation',
                                'Url': rule.url
                            }
                        }
                        
                    findings.append(finding)
                    
                    # Security Hub has a batch limit of 100 findings
                    if len(findings) >= 100:
                        try:
                            response = security_hub.batch_import_findings(Findings=findings)
                            _process_security_hub_response(response)
                            findings = []
                        except Exception as e:
                            console.print(f"[red]Error sending batch to Security Hub: {str(e)}[/red]")
        
        # Send any remaining findings
        if findings:
            try:
                response = security_hub.batch_import_findings(Findings=findings)
                _process_security_hub_response(response)
            except Exception as e:
                console.print(f"[red]Error sending final batch to Security Hub: {str(e)}[/red]")
                
        console.print("[green]Successfully exported failed checks to Security Hub[/green]")
        
    except Exception as e:
        console.print(f"[red]Error connecting to Security Hub: {str(e)}[/red]")

def _process_security_hub_response(response):
    """
    Process the response from Security Hub batch import
    """
    if response['FailedCount'] > 0:
        for failure in response['FailedFindings']:
            console.print(
                f"[yellow]Warning: Failed to import finding: {failure['Id']}, "
                f"Error: {failure['ErrorCode']} - {failure['ErrorMessage']}[/yellow]"
            )


def print_consolidated_results(rules: list):

    pillars = set([i.pillar for i in rules])

    for pillar in pillars:
        table = Table()
        table.add_column("Section")
        table.add_column("Namespace")
        table.add_column("Rule")
        table.add_column("Resource")
        table.add_column("Resource Type")
        table.add_column("Resolution")
        filtered_rules = [i for i in rules if i.pillar == pillar]
        for rule in filtered_rules:
            color = "red"
            namespace = "Cluster Wide"
            if rule.result.status:
                color = "green"
            if rule.result.namespace:
                namespace = rule.result.namespace
            for resource in rule.result.resources:
                table.add_row(
                    rule.section,
                    namespace,
                    rule.message,
                    resource,
                    rule.result.resource_type,
                    f"[link={rule.url}]Link[/link]",
                    style=color,
                )
        console.print(Panel(table, title=f"[cyan][bold]{pillar} rules"))
        console.print()


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
    export_txt: str = typer.Option(
        default=None,
        help="Export the report in txt format",
    ),
    export_csv: str = typer.Option(
        default=None,
        help="Export the report in csv format",
    ),
    export_html: str = typer.Option(
        default=None,
        help="Export the report in html format",
    ),
    export_json: str = typer.Option(
        default=None, help="Export the report in json format"
    ),
    export_security_hub: bool = typer.Option(
        False,
        "--export-security-hub",
        help="Export failed checks to AWS Security Hub (Security Hub must be enabled and have securityhub:GetFindings, securityhub:BatchImportFindings IAM permission)",
    ),
    insecure_skip_tls_verify: bool = typer.Option(
        False,
        "--insecure-skip-tls-verify",
    ),
    width: int = typer.Option(
        default=None, help="Width of the console (defaults to terminal width)"
    ),
    height: int = typer.Option(
        default=None,
        help="Height of the console (defaults to terminal height)",
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
        export-txt (str): Export the report in txt format
        export-csv (str): Export the report in csv format
        export-html (str): Export the report in html format
        export-json (str): Export the report in json format
        export-security-hub (str): Export the report to AWS Security Hub
        insecure-skip-tls-verify (str): Skip tls verification
        width (int): Output width
        height (int): Output height

    Returns:
        None

    """
    if insecure_skip_tls_verify:
        _add_tls_verify()
    else:
        # should pass in config file
        kubernetes.config.load_kube_config(context=context)

    if width:
        console.width = width
    if height:
        console.height = height

    context = _get_current_context(context)

    if not cluster:
        cluster = _get_cluster_name(context, region)

    if not region:
        region = _get_region()

    console.rule("[b]HARDENEKS", characters="*  ")
    console.print(f"You are operating at {region}")
    console.print(f"You context is {context}")
    console.print(f"Your cluster name is {cluster}")
    console.print(f"You are using {config} as your config file")
    console.print()

    with open(config, "r") as f:
        config = yaml.safe_load(f)

    if not namespace:
        namespaces = _get_namespaces(config["ignore-namespaces"])
    else:
        namespaces = [namespace]

    rules = config["rules"]

    resources = Resources(region, context, cluster, namespaces)
    resources.set_resources()

    results = []

    if "cluster_wide" in rules:
        cluster_wide_results = harden(resources, rules, "cluster_wide")
        results = results + cluster_wide_results

    if "namespace_based" in rules:
        for ns in namespaces:
            resources = NamespacedResources(region, context, cluster, ns)
            resources.set_resources()
            namespace_based_results = harden(resources, rules, "namespace_based")
            results = results + namespace_based_results

    print_consolidated_results(results)

    if export_txt:
        console.save_text(export_txt)
    if export_csv:
        _export_csv(results, export_csv)
    if export_html:
        console.save_html(export_html)
    if export_json:
        _export_json(results, export_json)
    if export_security_hub:
        _export_security_hub(results,region,context)
