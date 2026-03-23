#!/bin/bash
# Exit immediately if a command exits with a non-zero status
set -e

# Configuration
PROJECT_ID="gke-ai-eco-dev"
LOCATION="us-central1"
CLUSTER_NAME="tomer-barkland"
NAMESPACE="barkland"

echo "=== [1/5] Acquiring GKE cluster credentials ==="
gcloud container clusters get-credentials ${CLUSTER_NAME} --region ${LOCATION} --project ${PROJECT_ID}

echo "=== [2/5] Creating Namespace: ${NAMESPACE} ==="
kubectl create namespace ${NAMESPACE} --dry-run=client -o yaml | kubectl apply -f -

echo "=== [3/5] Building and Pushing Container Images ==="
# Execute existing image pushing automation
# Must be executed from the barkland repo root
if [ ! -f "Dockerfile" ]; then
    echo "Error: deploy.sh must be run from the repository root (e.g., ./scripts/deploy.sh)"
    exit 1
fi

./scripts/build_and_push.sh

echo "=== [4/5] Applying Kubernetes Manifests ==="
kubectl apply -f k8s/

echo "=== [5/5] Verifying Deployment Status ==="
kubectl rollout status deployment/barkland-orchestrator -n ${NAMESPACE}

echo "=== Barkland Deployment Complete! ==="
echo "You can check the external IP using:"
echo "kubectl get svc barkland-orchestrator -n ${NAMESPACE}"
