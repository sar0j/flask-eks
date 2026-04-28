# Flask EKS — Cloud Native Three-Tier Architecture

A production-grade cloud native application deployed on AWS EKS using modern DevOps practices including GitOps, Helm, Prometheus monitoring, and DevSecOps security scanning.

## Architecture
Developer
│
│ git push
▼
GitHub (flask-eks)
│                              │
│ GitHub Actions               │ ArgoCD watches
│ Test → SAST → Build          │ values.yaml changes
│ → Trivy Scan → Push ECR      │
▼                              ▼
Amazon ECR                   EKS Cluster (ap-southeast-2)
flask-app:sha    ──────────► three-tier namespace
│
┌─────────┴──────────┐
▼                    ▼
Flask Pod 1          Flask Pod 2
(ap-southeast-2a)    (ap-southeast-2b)
│
▼
RDS MySQL
(threetierdb)
│
▼
Prometheus + Grafana
(monitoring namespace)

## Tech Stack

| Layer | Technology |
|---|---|
| **Cloud** | AWS (ap-southeast-2) |
| **Container** | Docker + Amazon ECR |
| **Orchestration** | Kubernetes (EKS 1.31) |
| **Package Manager** | Helm 3 |
| **GitOps** | ArgoCD |
| **CI/CD** | GitHub Actions |
| **Security** | Trivy + Bandit + OPA Gatekeeper |
| **Monitoring** | Prometheus + Grafana |
| **App** | Python Flask REST API |
| **Database** | Amazon RDS MySQL |
| **Infrastructure** | Terraform (modular) |

## Repository Structure
flask-eks/
├── .github/
│   └── workflows/
│       └── deploy.yml        ← CI/CD + security pipeline
├── flask-chart/              ← Helm chart
│   ├── Chart.yaml
│   ├── values.yaml           ← default values (no secrets)
│   └── templates/
│       ├── _helpers.tpl
│       ├── namespace.yaml
│       ├── secret.yaml
│       ├── configmap.yaml
│       ├── deployment.yaml   ← non-root, resource limits
│       ├── service.yaml      ← Prometheus annotations
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
├── opa/                      ← OPA Gatekeeper policies
│   ├── require-resources.yaml
│   ├── no-root-containers.yaml
│   └── no-latest-tag.yaml
├── tests/
│   └── test_app.py           ← pytest unit tests
├── app.py                    ← Flask application
├── dockerfile                ← container definition
└── requirements.txt          ← Python dependencies

## CI/CD Security Pipeline

Every push to `main` runs a full secure pipeline:
git push
│
▼
GitHub Actions:

pytest tests          ← functionality
Bandit SAST scan      ← Python code security
docker build          ← create image
Trivy image scan      ← container vulnerabilities
Trivy K8s scan        ← manifest misconfigurations
docker push ECR       ← only if all scans pass
Update values.yaml    ← trigger ArgoCD
│
▼
ArgoCD detects values.yaml changed
│
▼
OPA Gatekeeper validates policies
│
▼
Zero downtime rolling deployment ✅


## Security Layers

| Layer | Tool | What it checks |
|---|---|---|
| Code | Bandit | Hardcoded secrets, SQL injection, debug mode |
| Container | Trivy | OS + Python package CVEs |
| Manifests | Trivy config | K8s misconfigurations |
| Runtime | OPA Gatekeeper | No root, resource limits, no latest tag |
| App | Input validation | Request size, required fields |
| Secrets | GitHub Secrets | Never committed to Git |

## Kubernetes Resources

| Resource | Description |
|---|---|
| `Namespace` | Isolated `three-tier` namespace |
| `Secret` | DB credentials (injected at runtime) |
| `ConfigMap` | Non-sensitive app configuration |
| `Deployment` | Flask app — non-root, read-only fs, resource limits |
| `Service` | LoadBalancer with Prometheus scrape annotations |
| `HPA` | Auto scales pods 2→6 based on CPU (50%) |
| `ServiceMonitor` | Prometheus scraping config |
| `PrometheusRule` | Alert rules for errors and latency |

## OPA Gatekeeper Policies

```bash
# Apply all policies
kubectl apply -f opa/

# Policies enforced:
# ✅ All containers must have CPU + memory limits
# ✅ No containers running as root
# ❌ No :latest tag (BLOCKED - deny mode)
```

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

### Install Prometheus + Grafana

```bash
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
- Flask App Metrics — request rate, error rate, latency

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
| POST | `/users` | Create a user (validates input) |
| DELETE | `/users/:id` | Delete a user |

## Quick Start

### Prerequisites
- AWS CLI configured
- kubectl installed
- Helm 3 installed
- ArgoCD CLI installed
- EKS cluster running

### Deploy Infrastructure

```bash
# Configure kubectl
aws eks update-kubeconfig \
  --name three-tier-eks \
  --region ap-southeast-2

# Install with Helm
helm install flask-app flask-chart \
  --namespace three-tier \
  --create-namespace \
  --set image.repository=YOUR-ECR-REPO \
  --set database.host=YOUR-RDS-ENDPOINT \
  --set database.password=YOUR-PASSWORD

# Apply OPA policies
kubectl apply -f opa/

# Install monitoring
helm install prometheus \
  prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace \
  --set grafana.adminPassword=YOUR-PASSWORD \
  --set grafana.service.type=LoadBalancer
```

### Verify

```bash
kubectl get pods -n three-tier
kubectl get svc -n three-tier
kubectl top pods -n three-tier
kubectl get hpa -n three-tier
kubectl get constraints -A
```

### Run Security Scans Locally

```bash
# Install tools
pip install bandit
brew install aquasecurity/trivy/trivy

# Scan Python code
bandit -r app.py

# Scan Docker image
docker build -t flask-app:local .
trivy image --severity HIGH,CRITICAL flask-app:local

# Scan K8s manifests
trivy config k8s/
trivy config flask-chart/
```

### Cleanup

```bash
helm uninstall flask-app --namespace three-tier
helm uninstall prometheus --namespace monitoring
kubectl delete -f opa/
```

## DevOps Concepts Demonstrated

| Concept | Implementation |
|---|---|
| GitOps | ArgoCD syncs Git → EKS automatically |
| Immutable infrastructure | Every deploy is a new image SHA tag |
| Zero downtime deployments | Rolling update strategy |
| Auto scaling | HPA scales pods based on CPU |
| Self healing | ArgoCD reverts manual cluster changes |
| Observability | Prometheus metrics + Grafana dashboards |
| Shift left security | Trivy + Bandit scan before push |
| Policy as code | OPA Gatekeeper enforces K8s policies |
| Least privilege | Non-root containers, dropped capabilities |
| Secret management | Secrets injected at runtime, never in Git |