import pytest
from kdoctor.ai.sanitizer import sanitize_data

def collect_pod_evidence(pods):
    """Extract useful diagnostic information from Kubernetes pods."""

    evidence = []

    for pod in pods:
        pod_status = pod.status
        container_statuses = (
            getattr(pod_status, "container_statuses", None) or []
        )

        containers = []

        for container in container_statuses:
            state = getattr(container, "state", None)
            waiting = getattr(state, "waiting", None)
            terminated = getattr(state, "terminated", None)

            containers.append({
                "name": container.name,
                "restart_count": container.restart_count,
                "ready": container.ready,
                "waiting_reason": getattr(waiting, "reason", None),
                "waiting_message": getattr(waiting, "message", None),
                "terminated_reason": getattr(terminated, "reason", None),
                "terminated_exit_code": getattr(terminated, "exit_code", None),
            })

        evidence.append({
            "name": pod.metadata.name,
            "namespace": pod.metadata.namespace,
            "phase": pod_status.phase,
            "containers": containers,
        })

    return evidence

def collect_deployment_evidence(deployments):
    """Extract useful diagnostic information from deployments."""

    evidence = []

    for deployment in deployments:
        spec = deployment.spec
        status = deployment.status

        desired = spec.replicas if spec.replicas is not None else 1
        ready = status.ready_replicas or 0
        available = status.available_replicas or 0
        updated = status.updated_replicas or 0

        evidence.append({
            "name": deployment.metadata.name,
            "namespace": deployment.metadata.namespace,
            "desired_replicas": desired,
            "ready_replicas": ready,
            "available_replicas": available,
            "updated_replicas": updated,
            "healthy": ready >= desired,
        })

    return evidence


def collect_node_evidence(nodes):
    """Extract useful diagnostic information from Kubernetes nodes."""

    evidence = []

    for node in nodes:
        node_conditions = (
            getattr(node.status, "conditions", None) or []
        )

        conditions = []

        ready = False

        for condition in node_conditions:
            conditions.append({
                "type": condition.type,
                "status": condition.status,
                "reason": getattr(condition, "reason", None),
                "message": getattr(condition, "message", None),
            })

            if condition.type == "Ready":
                ready = condition.status == "True"

        evidence.append({
            "name": node.metadata.name,
            "ready": ready,
            "conditions": conditions,
        })

    return evidence


def collect_event_evidence(events, limit=20):
    """Extract relevant warning events from Kubernetes."""

    if (
        not isinstance(limit, int)
        or isinstance(limit, bool)
        or limit < 0
    ):
        raise ValueError("limit must be a non-negative integer")

    evidence = []
    warning_events = [
        event for event in events
        if getattr(event, "type", None) == "Warning"
    ]

    # Keep the most recent events when timestamps are available.
    def event_timestamp(event):
        series = getattr(event, "series", None)
        metadata = getattr(event, "metadata", None)

        timestamps = (
            getattr(series, "last_observed_time", None),
            getattr(event, "event_time", None),
            getattr(event, "last_timestamp", None),
            getattr(event, "first_timestamp", None),
            getattr(metadata, "creation_timestamp", None),
        )

        timestamp = next(
            (value for value in timestamps if value is not None),
            None,
        )

        return timestamp.timestamp() if timestamp is not None else 0
    warning_events.sort(key=event_timestamp, reverse=True)

    for event in warning_events[:limit]:
        involved_object = getattr(event, "involved_object", None)

        evidence.append({
            "reason": getattr(event, "reason", None),
            "message": getattr(event, "message", None),
            "count": getattr(event, "count", None),
            "resource": {
                "kind": getattr(involved_object, "kind", None),
                "name": getattr(involved_object, "name", None),
                "namespace": getattr(involved_object, "namespace", None),
            } if involved_object else None,
        })

    return evidence


UNHEALTHY_WAITING_REASONS = {
    "CrashLoopBackOff",
    "ImagePullBackOff",
    "ErrImagePull",
    "CreateContainerConfigError",
    "CreateContainerError",
    "RunContainerError",
}


def collect_cluster_evidence(kube, namespace=None, event_limit=20):
    """Collect and sanitize diagnostic evidence from a Kubernetes cluster."""

    if not isinstance(event_limit, int) or isinstance(event_limit, bool) or event_limit < 0:
        raise ValueError("event_limit must be a non-negative integer")
    pods = collect_pod_evidence(
        kube.get_pods(namespace=namespace).items
    )

    deployments = collect_deployment_evidence(
        kube.get_deployments(namespace=namespace).items
    )

    nodes = collect_node_evidence(kube.get_nodes().items)

    raw_events = kube.get_events(namespace=namespace).items

    events = collect_event_evidence(
        raw_events,
        limit=event_limit,
    )
    

    # Keep only unhealthy pods.
    unhealthy_pods = []

    for pod in pods:
        pod_is_unhealthy = pod["phase"] not in ("Running", "Succeeded")

        for container in pod["containers"]:
            if (
                not container["ready"]
                or container["waiting_reason"] in UNHEALTHY_WAITING_REASONS
            ):
                pod_is_unhealthy = True
                break
        if namespace is None or pod["namespace"] == namespace:
            if pod_is_unhealthy:
                unhealthy_pods.append(pod)

    # Keep only deployments with unavailable replicas.
    unhealthy_deployments = [
        deployment
        for deployment in deployments
        if deployment["ready_replicas"] < deployment["desired_replicas"]
        and (
            namespace is None
            or deployment["namespace"] == namespace
        )
    ]

    # Keep nodes that are NotReady or reporting resource pressure.
    unhealthy_nodes = []

    for node in nodes:
        has_pressure = any(
            condition["type"] in {
                "MemoryPressure",
                "DiskPressure",
                "PIDPressure",
                "NetworkUnavailable",
            }
            and condition["status"] == "True"
            for condition in node["conditions"]
        )

        if not node["ready"] or has_pressure:
            unhealthy_nodes.append(node)

 
    evidence = {
        "nodes": unhealthy_nodes,
        "deployments": unhealthy_deployments,
        "pods": unhealthy_pods,
        "warning_events": events,
    }

    return sanitize_data(evidence)
