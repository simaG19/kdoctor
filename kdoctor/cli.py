import typer
from kdoctor.kube import KubeClient

app = typer.Typer()

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

    for node in nodes.items:
        ready_status ="unknown"
        for condition in node.status.conditions:
            if condition.type == "Ready":
                ready_status= condition.type
                break
                print(node.metadata.name, ready_status)
    


if __name__ == "__main__":
    app()