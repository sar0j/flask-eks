# Flask EKS — GitOps with Helm and ArgoCD

Production-grade Flask application deployed on AWS EKS using Helm, ArgoCD GitOps, and GitHub Actions CI/CD.

## Architecture
Developer pushes code
│
▼
GitHub Actions:

Run tests
Build Docker image
Push to ECR
Update values.yaml with new image tag
│
▼
ArgoCD detects values.yaml change
│
▼
Auto deploys to EKS (zero downtime) ✅


## Tech Stack

| Layer | Technology |
|---|---|
| **App** | Python Flask REST API |
| **Container** | Docker + Amazon ECR |
| **Orchestration** | Amazon EKS (Kubernetes 1.30) |
| **Package Manager** | Helm |
| **GitOps** | ArgoCD |
| **CI/CD** | GitHub Actions |
| **Auto Scaling** | Horizontal Pod Autoscaler (HPA) |
| **Infrastructure** | Terraform (separate repo) |

## Repository Structure
flask-eks/
├── .github/
│   └── workflows/
│       └── deploy.yml      ← CI/CD pipeline
├── flask-chart/            ← Helm chart
│   ├── Chart.yaml          ← chart metadata
│   ├── values.yaml         ← default values
│   └── templates/
│       ├── _helpers.tpl    ← reusable snippets
│       ├── namespace.yaml
│       ├── secret.yaml
│       ├── configmap.yaml
│       ├── deployment.yaml
│       ├── service.yaml
│       └── hpa.yaml
├── k8s/                    ← raw Kubernetes manifests
├── tests/
│   └── test_app.py         ← unit tests
├── app.py                  ← Flask application
├── dockerfile              ← container definition
└── requirements.txt        ← Python dependencies

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Home page |
| GET | `/health` | Health check |
| GET | `/users` | List all users |
| POST | `/users` | Create a user |
| DELETE | `/users/:id` | Delete a user |

## CI/CD Pipeline

Every push to `main` automatically:

1. Runs pytest unit tests
2. Builds Docker image
3. Pushes to Amazon ECR with commit SHA tag
4. Updates `flask-chart/values.yaml` with new image tag
5. Pushes updated values.yaml to GitHub
6. ArgoCD detects the change and deploys to EKS

## Helm Chart

### Install
```bash
helm install flask-app flask-chart \
  --namespace three-tier \
  --create-namespace \
  --set database.host=YOUR-RDS-ENDPOINT \
  --set database.password=YOUR-PASSWORD
```

### Upgrade
```bash
helm upgrade flask-app flask-chart \
  --namespace three-tier \
  --set image.tag=NEW-TAG
```

### Rollback
```bash
helm rollback flask-app 1 --namespace three-tier
```

### History
```bash
helm history flask-app --namespace three-tier
```

## ArgoCD GitOps

### Create Application
```bash
argocd app create flask-app \
  --repo https://github.com/sar0j/flask-eks.git \
  --path flask-chart \
  --dest-server https://kubernetes.default.svc \
  --dest-namespace three-tier \
  --helm-set database.host=YOUR-RDS-ENDPOINT \
  --helm-set database.password=YOUR-PASSWORD \
  --sync-policy automated \
  --auto-prune \
  --self-heal
```

### Check Status
```bash
argocd app get flask-app
argocd app sync flask-app
```

## Kubernetes Commands

```bash
# View all resources
kubectl get all -n three-tier

# View pods
kubectl get pods -n three-tier

# View logs
kubectl logs -f <pod-name> -n three-tier

# View HPA
kubectl get hpa -n three-tier

# Scale manually
kubectl scale deployment flask-app \
  --replicas=4 -n three-tier
```

## GitOps Workflow
Git is the source of truth:
values.yaml change → ArgoCD detects → auto deploys
Manual k8s change  → ArgoCD detects → auto reverts ← self healing!
Pod crashes        → K8s detects    → auto restarts ← self healing!
CPU > 50%          → HPA detects    → auto scales   ← auto scaling!

## Prerequisites

- AWS CLI configured
- kubectl installed
- Helm 3.x installed
- ArgoCD CLI installed
- eksctl installed
- Terraform installed

## Related Repositories

- [flask-three-tier](https://github.com/sar0j/flask-three-tier) — Docker + ECS + GitHub Actions
- [eks-three-tier](https://github.com/sar0j/eks-three-tier) — EKS + Terraform
