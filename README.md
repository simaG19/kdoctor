# kdoctor 🩺

[![PyPI version](https://badge.fury.io/py/kdoctor.svg)](https://badge.fury.io/py/kdoctor)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**`kdoctor`** is a lightweight, terminal-based CLI diagnostic and inspection tool for Kubernetes clusters built with Python, [Typer](https://typer.tiangolo.com/) and [Rich](https://github.com/Textualize/rich).

It provides instant visibility into cluster resources (**Nodes, Deployments, Pods, Events**) and runs automated diagnostic checks to detect cluster issues and surface actionable recommendations.

---

## ⚡ Features

- **Automated Diagnostics (`diagnose`)** – Executes a 5-point cluster health check covering:
  - Kubernetes API connectivity
  - Node readiness
  - Deployment replica health
  - Pod execution phases
  - Warning event detection

- **Targeted Resource Inspection**
  - Inspect a specific deployment
  - Inspect a specific pod
  - Automatically fetch recent pod logs

- **Rich Cluster Tables**
  - Nodes
  - Deployments
  - Pods
  - Events

- **Actionable Recommendations**
  - Aggregates detected issues
  - Suggests the next troubleshooting commands

---

# 📋 Prerequisites

Before using **kdoctor**, ensure you have:

1. Python **3.9+**
2. Access to a Kubernetes cluster
3. A valid Kubernetes configuration:

```
~/.kube/config
```

or the `KUBECONFIG` environment variable configured.

Supported clusters include:

- Minikube
- Amazon EKS
- Google GKE
- Azure AKS
- Any CNCF-compliant Kubernetes cluster

---

# 📦 Installation

## Option 1 – Install from PyPI (Recommended)

```bash
pip install kdoctor
```

### Windows Users

If `kdoctor` is not recognized after installation, add Python's **Scripts** directory to your PATH.

Example:

```
C:\Users\<User>\AppData\Local\Programs\Python\Python3x\Scripts
```

---

## Option 2 – Install with pipx

Install as an isolated CLI application:

```bash
pipx install kdoctor
```

---


# 🚀 Commands

## Diagnose Cluster

Runs a complete health scan.

```bash
kdoctor diagnose
```

Example output:

```text
Running cluster diagnostics...

✔ Kubernetes API reachable
✔ Nodes Healthy
❌ 1 Deployment(s) Not Ready
✔ All Pods Running
❌ 10 Warning Events detected

Diagnosis:
• 1 deployment(s) have unavailable replicas.

Recent Warning Events suggest:
Back-off restarting failed container storage-provisioner

Recommendation:
Inspect deployment status:

kdoctor deployment argocd-applicationset-controller -n argocd
```

---

## Inspect a Deployment

Shows deployment health and replica status.

```bash
kdoctor deployment <DEPLOYMENT_NAME> -n <NAMESPACE>
```

Example:

```bash
kdoctor deployment argocd-applicationset-controller -n argocd
```

Example output:

```text
Deployment Details

Name: argocd-applicationset-controller
Namespace: argocd

Replicas:
0/1 Ready
1 Updated

Status:
⚠ Degraded (Unavailable Replicas)
```

---

## Inspect a Pod

Displays pod information and fetches the latest logs.

```bash
kdoctor pod <POD_NAME> -n <NAMESPACE>
```

Example:

```bash
kdoctor pod coredns-7d764666f9-8p2xl -n kube-system
```

Example output:

```text
Pod Details

Name: coredns-7d764666f9-8p2xl
Namespace: kube-system

Phase:
Running

Node:
minikube

Fetching last 20 log lines...

[INFO] plugin/ready: Still waiting on: "kubernetes"
[INFO] CoreDNS-1.10.1
[INFO] plugin/kubernetes: CoreDNS is running
```

---

## List Deployments

Lists deployments across every namespace.

```bash
kdoctor deployments
```

Example:

```text
Kubernetes Deployments

Namespace      Deployment                              Replicas
---------------------------------------------------------------
argocd         argocd-applicationset-controller        0/1
argocd         argocd-server                           1/1
default        my-release-local-demo-app               2/2
kube-system    coredns                                 1/1
```

---

## List Pods

Lists all pods and their execution phase.

```bash
kdoctor pods
```

Example:

```text
Kubernetes Pod Registry

Namespace      Pod Name                                Status
--------------------------------------------------------------
argocd         argocd-server-xxxx                      Running
default        my-release-local-demo-app-xxxx          Running
kube-system    coredns-xxxx                            Running
kube-system    storage-provisioner                     CrashLoopBackOff
```

---

## List Nodes

Displays node information.

```bash
kdoctor nodes
```

Example:

```text
Cluster Nodes

Name        Status    Role            Internal IP      Version
---------------------------------------------------------------
minikube    Ready     control-plane   192.xxx.xx.2     v1.28.3
```

---

## View Cluster Events

Displays recent Kubernetes events.

```bash
kdoctor events
```

Example:

```text
Cluster Events

Namespace     Type      Reason      Message
----------------------------------------------
kube-system   Warning   BackOff     Back-off restarting...
default       Normal    Scheduled   Successfully assigned...
```

---

## Show Version

Displays the connected Kubernetes API version.

```bash
kdoctor version
```

Example:

```text
Kubernetes API Server Version: v1.28.3
```

---

# 📄 License

Distributed under the **MIT License**.

See the **LICENSE** file for more information.
