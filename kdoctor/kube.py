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
    
    def get_pods(self):
        return self.core.list_pod_for_all_namespaces()
    def get_deployments(self):
        return self.apps.list_deployment_for_all_namespaces()