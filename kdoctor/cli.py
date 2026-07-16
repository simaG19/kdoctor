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
        print(node.metadata.name)


if __name__ == "__main__":
    app()