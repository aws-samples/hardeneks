from ...resources import Resources
from rich.console import Console
from rich.panel import Panel
from rich import print
import kubernetes

console = Console()

def _get_version() -> str:
    client = kubernetes.client.VersionApi()
    version = client.get_code()
    return version

def check_EKS_version(resources: Resources):
    version = _get_version()
    major = int(version.major)
    minor = version.minor
    last_char = version.minor[-1]
    if last_char == "+":
        minor = int(version.minor[:-1])
    else:
        minor = int(minor)

    good = False

    if major >= 1 and minor >= 24:
        good = True

    if good == False:
        print(Panel("[red] Current Version == " + version.major + "." + version.minor + "", title="EKS Version Should be greater or equal too 1.24"))
        console.print()
    
    return good