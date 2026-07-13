import typer
from kdoctor.kube import connect

app = typer.Typer()
@app.command()
def cluster_info():

    api = connect()

    print("Connected to Kubernetes!")

if __name__ == "__main__":
    app()