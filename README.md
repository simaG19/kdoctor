# kdoctor 🩺

[![PyPI version](https://badge.fury.io/py/kdoctor.svg)](https://badge.fury.io/py/kdoctor)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**`kdoctor`** is a lightweight, terminal-based CLI diagnostic and inspection tool for Kubernetes clusters built with Python, [Typer](https://typer.tiangolo.com/), and [Rich](https://github.com/Textualize/rich).

It provides instant visibility into cluster resources (**Nodes, Deployments, Pods, Events**) and runs automated diagnostic checks to detect cluster issues and surface actionable recommendations.

---

## ⚡ Features

* **Automated Diagnostics (`diagnose`):** Executes a 5-point cluster health check (API reachability, node readiness, deployment state, pod phases, and warning event detection).
* **Targeted Resource Inspection:** Directly inspect single pods and deployments with recent log fetching and replica status.
* **Rich Cluster Tables:** View clean, color-coded summaries for Nodes, Pods, Deployments, and Events across all namespaces.
* **Actionable Recommendations:** Aggregates failures and outputs specific troubleshooting steps.

---

## 📋 Prerequisites

Before running `kdoctor`, ensure you have:
1. **Python 3.9 or higher** installed.
2. An active Kubernetes configuration file (`~/.kube/config`) or environment variable (`KUBECONFIG`) set up to communicate with your target cluster (e.g., Minikube, EKS, GKE, AKS).

---

## 📦 Installation & Setup

### Option 1: Install via PyPI (Recommended)

You can install `kdoctor` directly from [PyPI](https://pypi.org/project/kdoctor/):

```bash
pip install kdoctor
