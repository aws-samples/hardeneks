from rich.table import Table
from rich.console import Console

console = Console()


def print_role_table(roles, message, type):
    table = Table()

    table.add_column("Kind", style="cyan")
    table.add_column("Namespace", style="magenta")
    table.add_column("Name", style="green")

    for role in roles:
        table.add_row(type, role.metadata.namespace, role.metadata.name)

    console.print(message, style="red")
    console.print(table)
    console.print()


def print_instance_table(instances, message):
    table = Table()

    table.add_column("InstanceId", style="cyan")
    table.add_column("HttpPutResponseHopLimit", style="magenta")

    for instance in instances:
        table.add_row(
            instance["Instances"][0]["InstanceId"],
            str(
                instance["Instances"][0]["MetadataOptions"][
                    "HttpPutResponseHopLimit"
                ]
            ),
        )

    console.print(
        message,
        style="red",
    )
    console.print(table)
    console.print()


def print_pod_table(pods, message):
    table = Table()

    table.add_column("Kind", style="cyan")
    table.add_column("Namespace", style="magenta")
    table.add_column("Name", style="green")

    for pod in pods:
        table.add_row("Pod", pod.metadata.namespace, pod.metadata.name)

    console.print(
        message,
        style="red",
    )
    console.print(table)
    console.print()


def print_workload_table(workloads, message, kind):
    table = Table()

    table.add_column("Kind", style="cyan")
    table.add_column("Namespace", style="magenta")
    table.add_column("Name", style="green")

    for workload in workloads:
        table.add_row(
            kind, workload.metadata.namespace, workload.metadata.name
        )

    console.print(
        message,
        style="red",
    )
    console.print(table)
    console.print()
    console.print("*" * 100)


def print_namespace_table(namespaces, message):
    table = Table()

    table.add_column("Namespace", style="cyan")

    for namespace in namespaces:
        table.add_row(
            namespace,
        )

    console.print(
        message,
        style="red",
    )
    console.print(table)
    console.print()


def print_service_table(services, message):
    table = Table()

    table.add_column("Kind", style="cyan")
    table.add_column("Namespace", style="magenta")
    table.add_column("Name", style="green")

    for workload in services:
        table.add_row(
            "Service", workload.metadata.namespace, workload.metadata.name
        )

    console.print(
        message,
        style="red",
    )
    console.print(table)
    console.print()
