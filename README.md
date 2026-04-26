# Flask EKS — Cloud Native Three-Tier Architecture

A production-grade cloud native application deployed on AWS EKS using modern DevOps practices including GitOps, Helm, and full observability.

## Architecture
Developer
│
│ git push
▼
GitHub (flask-eks)
│                         │
│ GitHub Actions           │ ArgoCD watches
│ Test → Build → Push ECR  │ values.yaml changes
▼                         ▼
Amazon ECR              EKS Cluster (ap-southeast-2)
flask-app:sha    ──►    three-tier namespace
│
┌─────────┴──────────┐
▼                    ▼
Flask Pod 1          Flask Pod 2
(ap-southeast-2a)    (ap-southeast-2b)
│
▼
RDS MySQL
(threetierdb)

## Tech Stack

| Layer | Technology |
|---|---|
| **Cloud** | AWS (ap-southeast-2) |
| **Container** | Docker + Amazon ECR |
| **Orchestration** | Kubernetes (EKS 1.31) |
| **Package Manager** | Helm 3 |
| **GitOps** | ArgoCD |
| **CI/CD** | GitHub Actions |
| **Monitoring** | Prometheus + Grafana |
| **App** | Python Flask REST API |
| **Database** | Amazon RDS MySQL |
| **Infrastructure** | Terraform (modular) |

## Repository Structure
flask-eks/
├── .github/
│   └── workflows/
│       └── deploy.yml        ← CI/CD pipeline
├── flask-chart/              ← Helm chart
│   ├── Chart.yaml
│   ├── values.yaml           ← default values (no secrets)
│   └── templates/
│       ├── _helpers.tpl
│       ├── namespace.yaml
│       ├── secret.yaml
│       ├── configmap.yaml
│       ├── deployment.yaml
│       ├── service.yaml
│       ├── hpa.yaml
│       ├── servicemonitor.yaml
│       └── prometheusrule.yaml
├── k8s/                      ← raw Kubernetes manifests
│   ├── namespace.yaml
│   ├── secret.yaml
│   ├── configmap.yaml
│   ├── deployment.yaml
│   ├── service.yaml
│   └── hpa.yaml
├── tests/
│   └── test_app.py           ← pytest unit tests
├── app.py                    ← Flask application
├── dockerfile                ← container definition
└── requirements.txt          ← Python dependencies

## CI/CD Pipeline

Every push to `main` automatically:
git push
│
▼
GitHub Actions:

Run pytest tests
Build Docker image
Push to Amazon ECR (tagged with git SHA)
Update image tag in values.yaml
Push values.yaml back to GitHub
│
▼
ArgoCD detects values.yaml changed
│
▼
Auto deploys new image to EKS (zero downtime)


## Kubernetes Resources

| Resource | Description |
|---|---|
| `Namespace` | Isolated `three-tier` namespace |
| `Secret` | DB credentials (injected at runtime) |
| `ConfigMap` | Non-sensitive app configuration |
| `Deployment` | Flask app with rolling update strategy |
| `Service` | LoadBalancer exposing app to internet |
| `HPA` | Auto scales pods 2→6 based on CPU (50%) |
| `ServiceMonitor` | Prometheus scraping config |
| `PrometheusRule` | Alert rules for errors and latency |

## Helm Chart

```bash
# Install
helm install flask-app flask-chart \
  --namespace three-tier \
  --create-namespace \
  --set database.host=YOUR-RDS-ENDPOINT \
  --set database.password=YOUR-PASSWORD

# Upgrade
helm upgrade flask-app flask-chart \
  --namespace three-tier \
  --set image.tag=NEW-TAG

# Rollback
helm rollback flask-app 1 --namespace three-tier

# History
helm history flask-app --namespace three-tier
```

## GitOps with ArgoCD

```bash
# Create ArgoCD application
argocd app create flask-app \
  --repo https://github.com/sar0j/flask-eks.git \
  --path flask-chart \
  --dest-server https://kubernetes.default.svc \
  --dest-namespace three-tier \
  --sync-policy automated \
  --auto-prune \
  --self-heal

# Check status
argocd app get flask-app

# Manual sync
argocd app sync flask-app
```

## Monitoring

### Prometheus + Grafana

```bash
# Install monitoring stack
helm repo add prometheus-community \
  https://prometheus-community.github.io/helm-charts
helm repo update

helm install prometheus \
  prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --set grafana.adminPassword=YOUR-PASSWORD \
  --set grafana.service.type=LoadBalancer \
  --set prometheus.service.type=LoadBalancer
```

### Available Dashboards
- Node Exporter / Nodes — CPU, Memory, Disk, Network
- Kubernetes / Compute Resources / Cluster — cluster overview
- Kubernetes / Compute Resources / Pod — per pod metrics
- Flask App Metrics — custom request rate, error rate, latency

### Custom Prometheus Alerts
| Alert | Threshold |
|---|---|
| `HighErrorRate` | >0.1 errors/sec for 2 mins |
| `HighResponseTime` | >1 second for 2 mins |
| `PodDown` | <2 pods running for 1 min |

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Home page |
| GET | `/health` | Health check |
| GET | `/metrics` | Prometheus metrics |
| GET | `/users` | List all users |
| POST | `/users` | Create a user |
| DELETE | `/users/:id` | Delete a user |

## Quick Start

### Prerequisites
- AWS CLI configured
- kubectl installed
- Helm 3 installed
- ArgoCD CLI installed
- EKS cluster running

### Deploy

```bash
# 1. Configure kubectl
aws eks update-kubeconfig \
  --name three-tier-eks \
  --region ap-southeast-2

# 2. Install with Helm
helm install flask-app flask-chart \
  --namespace three-tier \
  --create-namespace \
  --set image.repository=YOUR-ECR-REPO \
  --set database.host=YOUR-RDS-ENDPOINT \
  --set database.password=YOUR-PASSWORD

# 3. Verify
kubectl get all -n three-tier
kubectl get hpa -n three-tier
```

### Verify

```bash
kubectl get pods -n three-tier
kubectl get svc -n three-tier
kubectl top pods -n three-tier
kubectl get hpa -n three-tier
```

### Cleanup

```bash
helm uninstall flask-app --namespace three-tier
helm uninstall prometheus --namespace monitoring
```

## Key DevOps Concepts Demonstrated

- **GitOps** — Git as single source of truth
- **Immutable infrastructure** — every deploy is a new image tag
- **Zero downtime deployments** — rolling update strategy
- **Auto scaling** — HPA scales pods based on CPU
- **Self healing** — ArgoCD reverts manual cluster changes
- **Observability** — metrics, dashboards and alerts
- **Security** — secrets never committed to Git