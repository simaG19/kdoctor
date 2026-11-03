import pytest
from types import SimpleNamespace
from kdoctor.ai.evidence import collect_node_evidence
from kdoctor.ai.evidence import collect_pod_evidence
from kdoctor.ai.evidence import collect_event_evidence
from kdoctor.ai.evidence import collect_cluster_evidence

def test_collect_pod_evidence():
    pod = SimpleNamespace(
        metadata=SimpleNamespace(
            name="backend-api",
            namespace="production",
        ),
        status=SimpleNamespace(
            phase="Running",
            container_statuses=[
                SimpleNamespace(
                    name="backend",
                    restart_count=8,
                    ready=False,
                    state=SimpleNamespace(
                        waiting=SimpleNamespace(
                            reason="CrashLoopBackOff",
                            message="Container keeps crashing",
                        ),
                        terminated=None,
                    ),
                )
            ],
        ),
    )

    result = collect_pod_evidence([pod])

    assert len(result) == 1
    assert result[0]["name"] == "backend-api"
    assert result[0]["namespace"] == "production"
    assert result[0]["phase"] == "Running"

    container = result[0]["containers"][0]

    assert container["name"] == "backend"
    assert container["restart_count"] == 8
    assert container["ready"] is False
    assert container["waiting_reason"] == "CrashLoopBackOff"
    assert container["waiting_message"] == "Container keeps crashing"


def test_collect_pod_evidence_without_container_statuses():
    pod = SimpleNamespace(
        metadata=SimpleNamespace(
            name="new-pod",
            namespace="default",
        ),
        status=SimpleNamespace(
            phase="Pending",
            container_statuses=None,
        ),
    )

    result = collect_pod_evidence([pod])

    assert result == [
        {
            "name": "new-pod",
            "namespace": "default",
            "phase": "Pending",
            "containers": [],
        }
    ]


def test_collect_pod_evidence_with_empty_list():
    assert collect_pod_evidence([]) == []


from kdoctor.ai.evidence import collect_deployment_evidence


def test_collect_deployment_evidence():
    deployment = SimpleNamespace(
        metadata=SimpleNamespace(
            name="backend-api",
            namespace="production",
        ),
        spec=SimpleNamespace(replicas=3),
        status=SimpleNamespace(
            ready_replicas=1,
            available_replicas=1,
            updated_replicas=1,
        ),
    )

    result = collect_deployment_evidence([deployment])

    assert len(result) == 1
    assert result[0]["name"] == "backend-api"
    assert result[0]["namespace"] == "production"
    assert result[0]["desired_replicas"] == 3
    assert result[0]["ready_replicas"] == 1
    assert result[0]["available_replicas"] == 1
    assert result[0]["updated_replicas"] == 1
    assert result[0]["healthy"] is False


def test_collect_healthy_deployment():
    deployment = SimpleNamespace(
        metadata=SimpleNamespace(
            name="frontend",
            namespace="default",
        ),
        spec=SimpleNamespace(replicas=2),
        status=SimpleNamespace(
            ready_replicas=2,
            available_replicas=2,
            updated_replicas=2,
        ),
    )

    result = collect_deployment_evidence([deployment])

    assert result[0]["healthy"] is True


def test_collect_deployment_evidence_with_empty_list():
    assert collect_deployment_evidence([]) == []



def test_collect_unhealthy_node_evidence():
    node = SimpleNamespace(
        metadata=SimpleNamespace(name="worker-1"),
        status=SimpleNamespace(
            conditions=[
                SimpleNamespace(
                    type="Ready",
                    status="False",
                    reason="KubeletNotReady",
                    message="Kubelet stopped posting node status",
                ),
                SimpleNamespace(
                    type="DiskPressure",
                    status="True",
                    reason="DiskSpaceLow",
                    message="Available disk space is low",
                ),
            ]
        ),
    )

    result = collect_node_evidence([node])

    assert len(result) == 1
    assert result[0]["name"] == "worker-1"
    assert result[0]["ready"] is False
    assert result[0]["conditions"][0]["type"] == "Ready"
    assert result[0]["conditions"][0]["status"] == "False"
    assert result[0]["conditions"][1]["type"] == "DiskPressure"
    assert result[0]["conditions"][1]["status"] == "True"


def test_collect_healthy_node_evidence():
    node = SimpleNamespace(
        metadata=SimpleNamespace(name="worker-2"),
        status=SimpleNamespace(
            conditions=[
                SimpleNamespace(
                    type="Ready",
                    status="True",
                    reason="KubeletReady",
                    message="kubelet is posting ready status",
                )
            ]
        ),
    )

    result = collect_node_evidence([node])

    assert result[0]["ready"] is True


def test_collect_node_evidence_with_empty_list():
    assert collect_node_evidence([]) == []



from datetime import datetime, timezone, timedelta


def test_collect_warning_events():
    now = datetime.now(timezone.utc)

    warning_event = SimpleNamespace(
        type="Warning",
        reason="BackOff",
        message="Container repeatedly failed to start",
        count=5,
        event_time=now,
        last_timestamp=None,
        first_timestamp=None,
        involved_object=SimpleNamespace(
            kind="Pod",
            name="backend-api",
            namespace="production",
        ),
    )

    normal_event = SimpleNamespace(
        type="Normal",
        reason="Started",
        message="Container started",
        count=1,
        event_time=now,
        last_timestamp=None,
        first_timestamp=None,
        involved_object=None,
    )

    result = collect_event_evidence([warning_event, normal_event])

    assert len(result) == 1
    assert result[0]["reason"] == "BackOff"
    assert result[0]["message"] == "Container repeatedly failed to start"
    assert result[0]["count"] == 5
    assert result[0]["resource"]["name"] == "backend-api"
    assert result[0]["resource"]["namespace"] == "production"


def test_collect_events_respects_limit():
    now = datetime.now(timezone.utc)

    events = [
        SimpleNamespace(
            type="Warning",
            reason=f"Warning-{i}",
            message=f"Event {i}",
            count=1,
            event_time=now + timedelta(seconds=i),
            last_timestamp=None,
            first_timestamp=None,
            involved_object=None,
        )
        for i in range(5)
    ]

    result = collect_event_evidence(events, limit=2)

    assert len(result) == 2
    assert result[0]["reason"] == "Warning-4"
    assert result[1]["reason"] == "Warning-3"

@pytest.mark.parametrize("limit", [-1, 1.5, "2", True])
def test_collect_event_evidence_rejects_invalid_limit(limit):
    with pytest.raises(
        ValueError,
        match="limit must be a non-negative integer",
    ):
        collect_event_evidence([], limit=limit)

def test_collect_events_sorts_by_series_last_observed_time():
    now = datetime.now(timezone.utc)

    repeated_event = SimpleNamespace(
        type="Warning",
        reason="RepeatedWarning",
        message="Container repeatedly failed",
        count=5,
        event_time=now,
        last_timestamp=None,
        first_timestamp=None,
        series=SimpleNamespace(
            last_observed_time=now + timedelta(minutes=10)
        ),
        involved_object=None,
    )

    recent_event = SimpleNamespace(
        type="Warning",
        reason="RecentWarning",
        message="A more recent warning",
        count=1,
        event_time=now + timedelta(minutes=5),
        last_timestamp=None,
        first_timestamp=None,
        series=None,
        involved_object=None,
    )

    result = collect_event_evidence([
        repeated_event,
        recent_event,
    ])

    assert result[0]["reason"] == "RepeatedWarning"
    assert result[1]["reason"] == "RecentWarning"

def test_collect_event_evidence_with_empty_list():
    assert collect_event_evidence([]) == []



class FakeKubeClient:
    """Simulate Kubernetes API responses without a real cluster."""

    def __init__(self, pods=None, deployments=None, nodes=None, events=None):
        self.pods = pods or []
        self.deployments = deployments or []
        self.nodes = nodes or []
        self.events = events or []

        self.requested_namespaces = {}

    def get_pods(self, namespace=None):
        self.requested_namespaces["pods"] = namespace
        items = [
            pod for pod in self.pods
            if namespace is None or pod.metadata.namespace == namespace
        ]
        return SimpleNamespace(items=items)

    def get_deployments(self, namespace=None):
        self.requested_namespaces["deployments"] = namespace
        items = [
            deployment for deployment in self.deployments
            if (
                namespace is None
                or deployment.metadata.namespace == namespace
            )
        ]
        return SimpleNamespace(items=items)

    def get_nodes(self):
        return SimpleNamespace(items=self.nodes)

    def get_events(self, namespace=None):
        self.requested_namespaces["events"] = namespace
        items = [
            event for event in self.events
            if (
                namespace is None
                or (
                    event.involved_object
                    and event.involved_object.namespace == namespace
                )
            )
        ]
        return SimpleNamespace(items=items)


def make_test_pod(
    name,
    namespace,
    phase="Running",
    waiting_reason=None,
    container_ready=None,
):
    waiting = (
        SimpleNamespace(
            reason=waiting_reason,
            message="Container failed",
        )
        if waiting_reason else None
    )

    return SimpleNamespace(
        metadata=SimpleNamespace(name=name, namespace=namespace),
        status=SimpleNamespace(
            phase=phase,
            container_statuses=[
                SimpleNamespace(
                    name="app",
                    restart_count=5,
                    ready=(
                        waiting_reason is None
                        if container_ready is None
                        else container_ready
                    ),
                    state=SimpleNamespace(
                        waiting=waiting,
                        terminated=None,
                    ),
                )
            ],
        ),
    )


def make_test_deployment(name, namespace, desired, ready):
    return SimpleNamespace(
        metadata=SimpleNamespace(name=name, namespace=namespace),
        spec=SimpleNamespace(replicas=desired),
        status=SimpleNamespace(
            ready_replicas=ready,
            available_replicas=ready,
            updated_replicas=ready,
        ),
    )

def test_collect_cluster_evidence_includes_running_pods_with_unready_containers():
    kube = FakeKubeClient(
        pods=[
            make_test_pod(
                "unready-api",
                "production",
                phase="Running",
                container_ready=False,
            )
        ]
    )

    result = collect_cluster_evidence(
        kube,
        namespace="production",
    )

    assert len(result["pods"]) == 1
    assert result["pods"][0]["name"] == "unready-api"
    assert result["pods"][0]["phase"] == "Running"
    assert result["pods"][0]["containers"][0]["ready"] is False

def make_test_node(name, ready, disk_pressure=False):
    conditions = [
        SimpleNamespace(
            type="Ready",
            status="True" if ready else "False",
            reason="KubeletReady" if ready else "KubeletNotReady",
            message="Node condition",
        )
    ]

    if disk_pressure:
        conditions.append(
            SimpleNamespace(
                type="DiskPressure",
                status="True",
                reason="DiskSpaceLow",
                message="Available disk space is low",
            )
        )

    return SimpleNamespace(
        metadata=SimpleNamespace(name=name),
        status=SimpleNamespace(conditions=conditions),
    )


def make_test_event(namespace, event_type="Warning", message="Pod warning"):
    return SimpleNamespace(
        type=event_type,
        reason="BackOff",
        message=message,
        count=1,
        event_time=None,
        last_timestamp=None,
        first_timestamp=None,
        involved_object=SimpleNamespace(
            kind="Pod",
            name="backend-api",
            namespace=namespace,
        ),
    )


def test_collect_cluster_evidence_filters_and_sanitizes():
    kube = FakeKubeClient(
        pods=[
            make_test_pod(
                "backend-api",
                "production",
                waiting_reason="CrashLoopBackOff",
            ),
            make_test_pod(
                "other-api",
                "default",
                waiting_reason="CrashLoopBackOff",
            ),
        ],
        deployments=[
            make_test_deployment("backend", "production", 3, 1),
            make_test_deployment("frontend", "default", 2, 0),
        ],
        nodes=[
            make_test_node("worker-1", ready=False),
            make_test_node("worker-2", ready=True, disk_pressure=True),
        ],
        events=[
            make_test_event(
                "production",
                message="password=topsecret-value",
            ),
            make_test_event("default"),
            make_test_event("production", event_type="Normal"),
        ],
    )
    result = collect_cluster_evidence(kube, namespace="production")
        # Verify namespace filtering is requested from the Kubernetes client.
    assert kube.requested_namespaces == {
        "pods": "production",
        "deployments": "production",
        "events": "production",
    }

    result = collect_cluster_evidence(kube, namespace="production")

    # Only unhealthy pods and deployments from production.
    assert [pod["name"] for pod in result["pods"]] == ["backend-api"]
    assert [deployment["name"] for deployment in result["deployments"]] == [
        "backend"
    ]

    # Nodes are cluster-scoped, so both unhealthy nodes are retained.
    assert [node["name"] for node in result["nodes"]] == [
        "worker-1",
        "worker-2",
    ]

    # Only production warning events are retained.
    assert len(result["warning_events"]) == 1
    assert result["warning_events"][0]["resource"]["namespace"] == "production"

    # Sensitive text is sanitized before returning the evidence.
    assert "topsecret-value" not in result["warning_events"][0]["message"]


def test_collect_cluster_evidence_empty_cluster():
    kube = FakeKubeClient()

    result = collect_cluster_evidence(kube)

    assert result == {
        "nodes": [],
        "deployments": [],
        "pods": [],
        "warning_events": [],
    }
