
from types import SimpleNamespace

from typer.testing import CliRunner

from kdoctor.cli import app

runner = CliRunner()


def test_help_command():
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "Usage" in result.output


def test_version_command(monkeypatch):
    class FakeKubeClient:
        def get_version(self):
            return SimpleNamespace(git_version="v1.30.0")

    monkeypatch.setattr("kdoctor.cli.KubeClient", FakeKubeClient)

    result = runner.invoke(app, ["version"])

    assert result.exit_code == 0
    assert "Git Version: v1.30.0" in result.output

def test_nodes_command(monkeypatch):
    ready_node = SimpleNamespace(
        metadata=SimpleNamespace(name="worker-1"),
        status=SimpleNamespace(
            conditions=[
                SimpleNamespace(type="Ready", status="True")
            ]
        )
    )

    not_ready_node = SimpleNamespace(
        metadata=SimpleNamespace(name="worker-2"),
        status=SimpleNamespace(
            conditions=[
                SimpleNamespace(type="Ready", status="False")
            ]
        )
    )

    class FakeKubeClient:
        def get_nodes(self):
            return SimpleNamespace(items=[ready_node, not_ready_node])

    monkeypatch.setattr("kdoctor.cli.KubeClient", FakeKubeClient)

    result = runner.invoke(app, ["nodes"])

    assert result.exit_code == 0
    assert "worker-1" in result.output
    assert "worker-2" in result.output
    assert "Ready" in result.output
    assert "NotReady" in result.output


def test_diagnose_healthy_cluster(monkeypatch):
    # Simulate one healthy Kubernetes node
    healthy_node = SimpleNamespace(
        status=SimpleNamespace(
            conditions=[
                SimpleNamespace(type="Ready", status="True")
            ]
        )
    )

    # Simulate one healthy deployment
    healthy_deployment = SimpleNamespace(
        metadata=SimpleNamespace(name="web-app"),
        spec=SimpleNamespace(replicas=2),
        status=SimpleNamespace(ready_replicas=2)
    )

    # Simulate one running pod
    healthy_pod = SimpleNamespace(
        metadata=SimpleNamespace(name="web-app-pod"),
        status=SimpleNamespace(phase="Running")
    )

    # Simulate no warning events
    normal_event = SimpleNamespace(
        type="Normal",
        message="Pod started successfully"
    )

    class FakeKubeClient:
        def get_nodes(self):
            return SimpleNamespace(items=[healthy_node])

        def get_deployments(self):
            return SimpleNamespace(items=[healthy_deployment])

        def get_pods(self):
            return SimpleNamespace(items=[healthy_pod])

        def get_events(self):
            return SimpleNamespace(items=[normal_event])

    monkeypatch.setattr("kdoctor.cli.KubeClient", FakeKubeClient)

    result = runner.invoke(app, ["diagnose"])

    assert result.exit_code == 0
    assert "Nodes Healthy" in result.output
    assert "Deployment Healthy" in result.output
    assert "All Pods Running" in result.output
    assert "No Warning Events" in result.output
    assert "Cluster is fully healthy!" in result.output

def test_diagnose_unhealthy_cluster(monkeypatch):
    # Simulate an unhealthy node
    unhealthy_node = SimpleNamespace(
        status=SimpleNamespace(
            conditions=[
                SimpleNamespace(type="Ready", status="False")
            ]
        )
    )

    # Simulate a degraded deployment
    unhealthy_deployment = SimpleNamespace(
        metadata=SimpleNamespace(name="api-deployment"),
        spec=SimpleNamespace(replicas=3),
        status=SimpleNamespace(ready_replicas=1)
    )

    # Simulate a failing pod
    # failing_pod = SimpleNamespace(
    #     metadata=SimpleNamespace(name="api-crash-pod"),
    #     status=SimpleNamespace(phase="CrashLoopBackOff")
    # )
    failing_pod = SimpleNamespace(
    metadata=SimpleNamespace(name="api-crash-pod"),
    status=SimpleNamespace(
        phase="Running",
        container_statuses=[
            SimpleNamespace(
                name="api",
                restart_count=5,
                state=SimpleNamespace(
                    waiting=SimpleNamespace(
                        reason="CrashLoopBackOff"
                    )
                )
            )
        ]
    )
)

    # Simulate a Kubernetes warning event
    warning_event = SimpleNamespace(
        type="Warning",
        message="Back-off restarting failed container"
    )

    class FakeKubeClient:
        def get_nodes(self):
            return SimpleNamespace(items=[unhealthy_node])

        def get_deployments(self):
            return SimpleNamespace(items=[unhealthy_deployment])

        def get_pods(self):
            return SimpleNamespace(items=[failing_pod])

        def get_events(self):
            return SimpleNamespace(items=[warning_event])

    monkeypatch.setattr("kdoctor.cli.KubeClient", FakeKubeClient)

    result = runner.invoke(app, ["diagnose"])

    assert result.exit_code == 0
    assert "1 Node(s) Not Ready" in result.output
    assert "1 Deployment(s) Not Ready" in result.output
    assert "1 unhealthy pod(s) detected" in result.output
    assert "Inspect failing pod: kdoctor pod api-crash-pod" in result.output
    assert "1 Warning Events detected" in result.output

    assert "Back-off restarting failed container" in result.output
    assert "api-crash-pod" in result.output
    assert "api-deployment" in result.output


def test_deployments_command(monkeypatch):
    healthy = SimpleNamespace(
        metadata=SimpleNamespace(name="frontend"),
        spec=SimpleNamespace(replicas=2),
        status=SimpleNamespace(ready_replicas=2)
    )

    degraded = SimpleNamespace(
        metadata=SimpleNamespace(name="backend"),
        spec=SimpleNamespace(replicas=3),
        status=SimpleNamespace(ready_replicas=1)
    )

    scaled_to_zero = SimpleNamespace(
        metadata=SimpleNamespace(name="worker"),
        spec=SimpleNamespace(replicas=0),
        status=SimpleNamespace(ready_replicas=0)
    )

    class FakeKubeClient:
        def get_deployments(self):
            return SimpleNamespace(
                items=[healthy, degraded, scaled_to_zero]
            )

    monkeypatch.setattr("kdoctor.cli.KubeClient", FakeKubeClient)

    result = runner.invoke(app, ["deployments"])

    assert result.exit_code == 0
    assert "frontend" in result.output
    assert "Healthy" in result.output
    assert "backend" in result.output
    assert "Degraded (1/3)" in result.output
    assert "worker" in result.output
    assert "Scaled to 0" in result.output

def test_pods_command(monkeypatch):
    running_pod = SimpleNamespace(
        metadata=SimpleNamespace(
            name="frontend-pod",
            namespace="production"
        ),
        status=SimpleNamespace(phase="Running")
    )

    pending_pod = SimpleNamespace(
        metadata=SimpleNamespace(
            name="backend-pod",
            namespace="staging"
        ),
        status=SimpleNamespace(phase="Pending")
    )

    class FakeKubeClient:
        def get_pods(self):
            return SimpleNamespace(
                items=[running_pod, pending_pod]
            )

    monkeypatch.setattr("kdoctor.cli.KubeClient", FakeKubeClient)

    result = runner.invoke(app, ["pods"])

    assert result.exit_code == 0
    assert "frontend-pod" in result.output
    assert "backend-pod" in result.output
    assert "production" in result.output
    assert "staging" in result.output
    assert "Running" in result.output
    assert "Pending" in result.output

def test_ai_diagnose_declined_by_user(monkeypatch):
    from unittest.mock import Mock

    mock_diagnose = Mock()

    monkeypatch.setattr(
        "kdoctor.cli.KubeClient",
        Mock()
    )

    monkeypatch.setattr(
        "kdoctor.cli.diagnose_cluster",
        mock_diagnose,
    )

    result = runner.invoke(
        app,
        ["ai", "diagnose"],
        input="n\n",
    )

    assert result.exit_code != 0
    assert "Send sanitized Kubernetes evidence to Google Gemini?" in result.output
    mock_diagnose.assert_not_called()
def test_ai_diagnose_accepted_by_user(monkeypatch):
    from unittest.mock import Mock

    mock_diagnose = Mock(return_value="No critical issues found.")

    mock_kube = Mock()
    mock_gemini = Mock()

    class FakeGeminiClient:
        def __enter__(self):
            return mock_gemini

        def __exit__(self, exc_type, exc_value, traceback):
            pass

    monkeypatch.setattr("kdoctor.cli.KubeClient", lambda: mock_kube)
    monkeypatch.setattr("kdoctor.cli.GeminiClient", FakeGeminiClient)
    monkeypatch.setattr("kdoctor.cli.diagnose_cluster", mock_diagnose)

    result = runner.invoke(
        app,
        [
            "ai",
            "diagnose",
            "--namespace",
            "default",
            "--event-limit",
            "5",
        ],
        input="y\n",
    )

    assert result.exit_code == 0
    assert "No critical issues found." in result.output

    mock_diagnose.assert_called_once_with(
        mock_kube,
        mock_gemini,
        namespace="default",
        event_limit=5,
    )