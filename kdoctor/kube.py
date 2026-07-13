from kubernetes import client, config

class KubeClient:

    def __init__(self):
        config.load_kube_config()

        self.core = client.CoreV1Api()

        self.version = client.VersionApi()
    
    def get_version(self):
        return self.version.get_code()