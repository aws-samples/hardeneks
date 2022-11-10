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
