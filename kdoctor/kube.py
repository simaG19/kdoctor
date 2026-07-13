from kubernetes import client, config

def connect():
    config.load_kube_config()
    return client.CoreV1Api()

def get_version():
    config.load_kube_config()

    version_api = client.VersionApi()

    return version_api.get_code()