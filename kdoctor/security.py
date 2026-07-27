from typing import Dict, List
from kubernetes import client, config
from rich.console import Console
from rich.table import Table

console = Console()

def load_k8s_config():
    """Load kubeconfig or in-cluster configuration safely."""
    try:
        config.load_kube_config()
    except config.ConfigException:
        try:
            config.load_incluster_config()
        except config.ConfigException as e:
            console.print("[bold red]Error loading kubeconfig:[/bold red] Active cluster context not found.")
            raise e

def run_security_scan(namespace: str = None):
    """Scan cluster workloads for common security misconfigurations."""
    console.print("\n[bold cyan]🔒 Running DevSecOps Security & Compliance Audit...[/bold cyan]\n")
    
    # Ensure active kubeconfig is loaded into the client context
    try:
        load_k8s_config()
    except Exception:
        return

    v1 = client.CoreV1Api()

    try:
        if namespace:
            pods = v1.list_namespaced_pod(namespace).items
        else:
            pods = v1.list_pod_for_all_namespaces().items
    except Exception as e:
        console.print(f"[bold red]Error fetching pods for security scan:[/bold red] {e}")
        return

    table = Table(title="Security & Compliance Audit Results", show_lines=True)
    table.add_column("Namespace", style="cyan")
    table.add_column("Pod / Container", style="bold white")
    table.add_column("Root User", style="bold red")
    table.add_column("Resource Limits", style="yellow")
    table.add_column("Image Tag", style="magenta")

    issue_count = 0

    for pod in pods:
        pod_name = pod.metadata.name
        ns = pod.metadata.namespace
        pod_spec = pod.spec

        # Pod-level security context
        pod_sec_context = pod_spec.security_context or client.V1PodSecurityContext()

        for container in pod_spec.containers:
            c_name = container.name
            c_sec_context = container.security_context or client.V1SecurityContext()

            # 1. Check Root Execution
            run_as_non_root = c_sec_context.run_as_non_root if c_sec_context.run_as_non_root is not None else pod_sec_context.run_as_non_root
            run_as_user = c_sec_context.run_as_user if c_sec_context.run_as_user is not None else pod_sec_context.run_as_user
            
            is_root = True
            if run_as_non_root or (run_as_user is not None and run_as_user > 0):
                is_root = False

            root_status = "❌ Allowed (Root)" if is_root else "✔ Non-Root"

            # 2. Check Resource Limits
            resources = container.resources or client.V1ResourceRequirements()
            has_limits = bool(resources.limits)
            has_requests = bool(resources.requests)
            
            if has_limits and has_requests:
                limits_status = "✔ Set"
            elif has_limits or has_requests:
                limits_status = "⚠ Partial"
            else:
                limits_status = "❌ Missing"

            # 3. Check Image Tag
            image = container.image or ""
            if ":" not in image or image.endswith(":latest"):
                tag_status = "❌ Uses :latest"
            else:
                tag_status = "✔ Tagged"

            # Log container issues
            if is_root or limits_status != "✔ Set" or "❌" in tag_status:
                issue_count += 1
                table.add_row(
                    ns,
                    f"{pod_name}\n└─ [dim]{c_name}[/dim]",
                    root_status,
                    limits_status,
                    tag_status
                )

    if issue_count == 0:
        console.print("[bold green]✔ Great job! No security issues detected across scanned pods.[/bold green]\n")
    else:
        console.print(table)
        console.print(f"\n[bold yellow]Found {issue_count} container(s) with security warnings.[/bold yellow]\n")