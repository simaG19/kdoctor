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

@app.command()
def pods():
       kube = KubeClient()
       pods = kube.get_pods() 
       table = Table(title="Kubernetes pod Registry")
       
       
       table.add_column("POd Name Space", style="cyan", no_wrap=True)
       table.add_column("POd Name", style="cyan", no_wrap=True)
       table.add_column("Status", justify="center")
       
       for pod in pods.items:
           pod_name = pod.metadata.name
           pod_namespace = pod.metadata.namespace

           pod_status =pod.status.phase
           table.add_row(pod_namespace,pod_name,pod_status)
       console.print(table)

@app.command()
def deployments():
    kube = KubeClient()
    deployments = kube.get_deployments() 
    table = Table(title="Kubernetes Deployment Registry")
     
     # Deployment       ┃ Desired  ┃ Ready  ┃ Health  
    table.add_column("Deployment", style="cyan", no_wrap=True)
    table.add_column("Desired", style="cyan", no_wrap=True)
    table.add_column("Ready", justify="center")
    table.add_column("Health")

    for deployment in deployments.items:
        name= deployment.metadata.name
        desired = deployment.spec.replicas or 0
        ready = deployment.status.ready_replicas or 0
    
    
        if desired == 0: 
            health = "Scaled to 0"
        elif ready == desired:
            health = "Healthy"
        else:
            health = f"🔴 Degraded ({ready}/{desired})"
        
        table.add_row(name,str(desired), str(ready),health)
    console.print(table)

@app.command()
def events():
    kube = KubeClient()
    events = kube.get_events() 
    table = Table(title="Kubernetes Events")
     
    table.add_column("Type", style="cyan", no_wrap=True)
    table.add_column("Object", style="cyan", no_wrap=True)
    table.add_column("Reason")
    table.add_column("Message")

    for event in events.items:
        event_type = event.type
        name= event.involved_object.name
        reason= event.reason
        message= event.message
        if event_type == "Warning":
            color ="red"
        else:
            color ="green"

        table.add_row( f"[{color}]{event_type}[/{color}]",name,reason,message)
    console.print(table)





if __name__ == "__main__":
    app()