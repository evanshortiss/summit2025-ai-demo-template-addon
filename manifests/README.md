# LangChain Agent Python - OpenShift Manifests

This directory contains the manifests needed to build and deploy the LangChain AI Agent Python application using OpenShift Pipelines (Tekton) and OpenShift GitOps (ArgoCD).

## Directory Structure

```
manifests/
├── argocd/                          # ArgoCD Applications
│   ├── langchain-agent-argocd-app-dev.yaml        # App deployment
│   └── langchain-agent-argocd-app-dev-build.yaml  # Build pipeline
└── helm/
    ├── app/                         # Application Helm Chart
    │   ├── Chart.yaml
    │   ├── values.yaml
    │   └── templates/
    │       ├── _helpers.tpl
    │       ├── deployment.yaml
    │       ├── service.yaml
    │       ├── serviceaccount.yaml
    │       └── route.yaml
    └── build/                       # Build Pipeline Helm Chart
        ├── Chart.yaml
        ├── values.yaml
        └── templates/
            ├── _helpers.tpl
            ├── pipeline-build.yaml
            ├── task-update-deployment.yaml
            ├── eventlistener.yaml
            ├── triggerbinding-commit.yaml
            ├── triggertemplate-build.yaml
            ├── serviceaccount-pipeline.yaml
            ├── route.yaml
            └── pipelinerun-init.yaml
```

## Features

This simplified manifest set provides:

1. **Build Pipeline**: 
   - Git clone from source repository
   - Container image build using Buildah
   - Deployment update trigger
   - No scanning or signing steps (simplified for demo)

2. **Deployment**:
   - Kubernetes Deployment with health checks
   - Service for internal communication
   - OpenShift Route for external access
   - Service Account with appropriate permissions

3. **GitOps Integration**:
   - ArgoCD Applications for both build and app deployment
   - Automatic sync from Git repository
   - Build pipeline triggered by Git webhooks

## Configuration

The application can be configured through the Helm values files:

### Application Configuration (`helm/app/values.yaml`)
- `image.registry`, `image.organization`, `image.name`: Container image details
- `env`: Environment variables for the Python application
- `resources`: CPU and memory limits/requests
- `service.port`: Service port (default: 8080)

### Build Configuration (`helm/build/values.yaml`)
- `git.repo`: Source repository URL
- `git.branch`: Git branch to build from (default: main)
- `image.*`: Target image registry and organization

## Deployment

1. Deploy the build pipeline:
   ```bash
   oc apply -f argocd/langchain-agent-argocd-app-dev-build.yaml
   ```

2. Deploy the application:
   ```bash
   oc apply -f argocd/langchain-agent-argocd-app-dev.yaml
   ```

## Notes

- The build pipeline uses OpenShift Pipelines (Tekton)
- Deployment is managed by OpenShift GitOps (ArgoCD)
- The application expects a Python container image with the LangChain agent code
- Health checks are configured for `/health` endpoint on port 8080