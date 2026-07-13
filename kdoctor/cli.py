import typer
from kdoctor.kube import connect, get_version

app = typer.Typer()
@app.command()
def cluster_info():

    api = connect()

    print("Connected to Kubernetes!")

def version():

    version = get_version()

    print(f"Major: {version.major}")
    print(f"Minor: {version.minor}")
    print(f"Git Version: {version.git_version}")
    print(f"Platform: {version.platform}")

if __name__ == "__main__":
    app()