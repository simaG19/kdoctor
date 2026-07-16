import typer
from rich.console import Console
from rich.table import Table
from kdoctor.kube import KubeClient
app = typer.Typer()
console = Console()

@app.command()
def version():
    kube = KubeClient()
    version = kube.get_version()
    # nodes = 
    print(f"Git Version: {version.git_version}")


@app.command()
def nodes():
    kube = KubeClient()
    nodes = kube.get_nodes()
    
    table = Table(title="Kubernetes Node Registry")
    
    table.add_column("Node Name", style="cyan", no_wrap=True)
    table.add_column("Status", justify="center")

    for node in nodes.items:
        node_name = node.metadata.name
        ready_status ="unknown"
        status_color = "yellow"

        for condition in node.status.conditions:
            if condition.type == "Ready":
                if condition.status == "True":
                    ready_status = "Ready"
                    status_color = "green"
                else:
                    ready_status = "NotReady"
                    status_color = "red"
                break

                
        table.add_row(node_name, f"[{status_color}]{ready_status}[/{status_color}]")
    console.print(table)        


if __name__ == "__main__":
    app()