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

@app.command()
def pod(name: str, namespace: str = "default"):
    """Inspect a specific pod and fetch its recent logs."""
    kube = KubeClient()
    try:
        pod_info = kube.get_pod(name, namespace)
        console.print(f"\n[bold cyan]Pod Details: {name}[/bold cyan]")
        console.print(f"Namespace: {pod_info.metadata.namespace}")
        console.print(f"Phase: {pod_info.status.phase}")
        console.print(f"Node: {pod_info.spec.node_name}")
        
        console.print("\n[bold]Fetching recent logs (last 20 lines)...[/bold]")
        logs = kube.get_pod_logs(name, namespace)
        console.print(f"[dim]{logs}[/dim]")
    except Exception as e:
        console.print(f"[red]Error inspecting pod '{name}': {e}[/red]")


@app.command()
def deployment(name: str, namespace: str = "default"):
    """Inspect a specific deployment state."""
    kube = KubeClient()
    try:
        dep = kube.get_deployment(name, namespace)
        desired = dep.spec.replicas or 0
        ready = dep.status.ready_replicas or 0
        updated = dep.status.updated_replicas or 0
        
        console.print(f"\n[bold cyan]Deployment Details: {name}[/bold cyan]")
        console.print(f"Namespace: {dep.metadata.namespace}")
        console.print(f"Replicas: {ready}/{desired} Ready ({updated} updated)")
        
        if ready < desired:
            console.print("[red]⚠ Status: Degraded (Unavailable Replicas)[/red]")
        else:
            console.print("[green]✔ Status: Healthy[/green]")
    except Exception as e:
        console.print(f"[red]Error inspecting deployment '{name}': {e}[/red]")

@app.command()
def diagnose():
    kube = KubeClient()
    nodes = kube.get_nodes()
    
    console.print("Running cluster diagnostics...\n")
    console.print("[green]✔[/green] Kubernetes API reachable")
    issues = []
    unhealthy_nodes = 0
    
    for node in nodes.items:
        is_ready = False
        for condition in node.status.conditions:
            if condition.type == "Ready":
                is_ready = (condition.status == "True")
                break
        
        if not is_ready:
            unhealthy_nodes += 1

   
    if unhealthy_nodes == 0:
        console.print("[green]✔[/green] Nodes Healthy")
    else:
        console.print(f"[red]X {unhealthy_nodes} Node(s) Not Ready[/red]")
    if unhealthy_nodes > 0:
        issues.append(f"{unhealthy_nodes} node(s) are in NotReady state.")
    
    # Deployment check
    deployments= kube.get_deployments()
    unhealthy_deployments = 0
    unhealthy_dep_names = []
    for deployment in deployments.items:
        desired = deployment.spec.replicas or 0
        ready = deployment.status.ready_replicas or 0
        
        if desired > ready:
            unhealthy_deployments +=1
            unhealthy_dep_names.append(deployment.metadata.name)
            
    if unhealthy_deployments == 0:
        console.print("[green]✔[/green] Deployment Healthy")
    else:
        console.print(f"[red]X {unhealthy_deployments} Deployment(s) Not Ready[/red]")
    if unhealthy_deployments > 0:
        issues.append(f"{unhealthy_deployments} deployment(s) have unavailable replicas.")

    #Pods Check
    pods= kube.get_pods()
    unhealthy_pods =0
    failing_pod_names = []
    for pod in pods.items:
        if pod.status.phase not in ("Running", "Succeeded"):
            unhealthy_pods +=1
            pod_name = pod.metadata.name
            failing_pod_names.append(pod_name)
    if unhealthy_pods == 0:
        console.print("[green]✔[/green] All Pods Running")
    else:
        console.print(f"[red]⚠ {unhealthy_pods} Pods Not Running[/red]")
    if unhealthy_pods > 0:
        issues.append("The cluster has unhealthy Pods.")

    #Check events
    events = kube.get_events()
    recent_warnings = []

    for event in events.items:
        if event.type == "Warning":
            recent_warnings.append(event.message)
    
    if len(recent_warnings) == 0:
        console.print("[green]✔[/green] No Warning Events")
    else:
        console.print(f"[red]❌[/red] {len(recent_warnings)} Warning Events detected")
    if issues or recent_warnings:
        console.print("\n[bold red]Diagnosis:[/bold red]")
        for issue in issues:
            console.print(f"• {issue}")
       
        if recent_warnings:
            console.print("\nRecent Warning Events suggest:")
            console.print(f"  [yellow]{recent_warnings[-1]}[/yellow]")
        
        console.print("\n[bold cyan]Recommendation:[/bold cyan]")
        
        if failing_pod_names:
            for pod in failing_pod_names:
                console.print(f"  • Inspect failing pod: [bold yellow]kdoctor pod {pod}[/bold yellow]")
        if unhealthy_dep_names:
            for dep in unhealthy_dep_names:
                console.print(f"  • Inspect deployment status: [bold yellow]kdoctor deployment {dep}[/bold yellow]")
        if unhealthy_nodes > 0:
            console.print("  [dim]• Describe node details or run: kubectl describe node <node-name>[/dim]")

    else:
        console.print("\n[bold green]✨ Cluster is fully healthy! No action required.[/bold green]")



from kdoctor.security import run_security_scan

@app.command()
def security(
    namespace: str = typer.Option(
        None, "--namespace", "-n", help="Filter security scan by specific namespace"
    )
):
    """Audit cluster workloads for root containers, missing resource limits, and :latest image tags."""
    run_security_scan(namespace=namespace)
    
if __name__ == "__main__":
    app()