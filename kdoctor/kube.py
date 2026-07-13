from kubernetes import client, config

def connect():
    config.load_kube_config() #It reads:~/.kube/config
    api = client.CoreV1Api()
    return api