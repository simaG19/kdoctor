
from unittest.mock import Mock

from kdoctor.kube import KubeClient


def create_kube_client():
    """Create a KubeClient without loading a real Kubernetes config."""

    kube = KubeClient.__new__(KubeClient)
    kube.core = Mock()
    kube.apps = Mock()

    return kube


def test_get_pods_in_namespace():
    kube = create_kube_client()

    kube.get_pods(namespace="production")

    kube.core.list_namespaced_pod.assert_called_once_with(
        namespace="production"
    )


def test_get_pods_across_all_namespaces():
    kube = create_kube_client()

    kube.get_pods()

    kube.core.list_pod_for_all_namespaces.assert_called_once_with()


def test_get_deployments_in_namespace():
    kube = create_kube_client()

    kube.get_deployments(namespace="production")

    kube.apps.list_namespaced_deployment.assert_called_once_with(
        namespace="production"
    )


def test_get_deployments_across_all_namespaces():
    kube = create_kube_client()

    kube.get_deployments()

    kube.apps.list_deployment_for_all_namespaces.assert_called_once_with()


def test_get_events_in_namespace():
    kube = create_kube_client()

    kube.get_events(namespace="production")

    kube.core.list_namespaced_event.assert_called_once_with(
        namespace="production"
    )


def test_get_events_across_all_namespaces():
    kube = create_kube_client()

    kube.get_events()

    kube.core.list_event_for_all_namespaces.assert_called_once_with()
