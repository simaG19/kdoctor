# kdoctor 🩺

`kdoctor` is a lightweight, terminal-based CLI diagnostic and inspection tool for Kubernetes clusters built with Python, [Typer](https://typer.tiangolo.com/), and [Rich](https://rich.readthedocs.io/).

It provides instant visibility into cluster resources (Nodes, Deployments, Pods, Events) and runs automated diagnostic checks to detect cluster issues and surface actionable recommendations.

---

## Features

* **Cluster Inspection Tables:** View clean, color-coded tables for Nodes, Pods, Deployments, and Events.
* **Automated Diagnostics (`diagnose`):** Performs a 5-point health check across your cluster:
  1. API Reachability
  2. Node Readiness
  3. Deployment Replicas
  4. Pod Execution Phases
  5. Warning Event Detection
* **Actionable Recommendations:** Aggregates discovered cluster issues and surfaces recent warning messages directly in your terminal.

---

### Prerequisites

* Python 3.9+
* A active `kubectl` context configured (e.g., `~/.kube/config` or active cluster session)
