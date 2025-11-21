# Django App Operator

A Kubernetes operator for managing Django applications using Kopf.

## Overview

This operator watches for `DjangoApp` custom resources and automatically creates and manages:
- Deployment (runs the Django application)
- HorizontalPodAutoscaler (manages scaling)
- Service (exposes the deployment internally)
- Ingress (exposes the service externally)

## Project Structure

```
djangoapp-operator/
├── operator.py              # Main Kopf handlers
├── builders/
│   ├── __init__.py         # Package initialization
│   ├── deployment.py       # DeploymentBuilder class
│   ├── hpa.py             # HPABuilder class
│   ├── service.py         # ServiceBuilder class
│   └── ingress.py         # IngressBuilder class
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Install the CRD
kubectl apply -f djangoapp-crd.yaml

# Run the operator
kopf run main.py --verbose
```

## Usage

Create a DjangoApp resource:

```yaml
apiVersion: faultycloud.io/v1alpha1
kind: DjangoApp
metadata:
  name: my-app
spec:
  deployment:
    image: myregistry/django-app:v1.0
    port: 8000
    resources:
      requests:
        cpu: "100m"
        memory: "128Mi"
      limits:
        cpu: "500m"
        memory: "512Mi"
  ingress:
    ingressClassName: nginx
    host: myapp.example.com
  autoscale:
    min: 2
    max: 10
    targetCPUUtilizationPercentage: 70
  env:
    - name: DEBUG
      value: "false"
```

## Design Principles

- Each builder validates its own inputs
- Builders receive only the data they need
- Kopf handles owner references via `kopf.adopt()`
- Resource names include descriptive suffixes