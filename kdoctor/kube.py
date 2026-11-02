from kubernetes import client, config


class KubeClient:

    def __init__(self):
        config.load_kube_config()

        self.core = client.CoreV1Api()
        self.version_api = client.VersionApi()
        self.apps = client.AppsV1Api()

    def get_version(self):
        return self.version_api.get_code()
    
    def get_nodes(self):
        return self.core.list_node()
    
    def get_pods(self, namespace=None):
        if namespace:
            return self.core.list_namespaced_pod(namespace=namespace)
        return self.core.list_pod_for_all_namespaces()
    
    def get_deployments(self, namespace=None):
        if namespace:
            return self.apps.list_namespaced_deployment(namespace=namespace)
        return self.apps.list_deployment_for_all_namespaces()
    def get_services(self):
        return self.core.list_service_for_all_namespaces()

    def get_events(self, namespace=None):
        if namespace:
            return self.core.list_namespaced_event(namespace=namespace)
        return self.core.list_event_for_all_namespaces()

    def get_pod(self, name: str, namespace: str = "default"):
        return self.core.read_namespaced_pod(name=name, namespace=namespace)

    def get_pod_logs(self, name: str, namespace: str = "default", tail_lines: int = 20):
        return self.core.read_namespaced_pod_log(name=name, namespace=namespace, tail_lines=tail_lines)
    
    def get_deployment(self, name: str, namespace: str = "default"):
        return self.apps.read_namespaced_deployment(name=name, namespace=namespace)