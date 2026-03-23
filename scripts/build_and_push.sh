#!/bin/bash
# Exit immediately if a command exits with a non-zero status
set -e

PROJECT_ID="gke-ai-eco-dev"
LOCATION="us-central1"
REPO="barkland"
IMAGE_PREFIX="${LOCATION}-docker.pkg.dev/${PROJECT_ID}/${REPO}"
IMAGE_TAG="latest"

echo "Copying Sandbox Python SDK client..."
cp -r ../agent-sandbox/clients/python/agentic-sandbox-client ./agentic-sandbox-client

echo "Building and Pushing Unified Barkland Image..."
docker build --push -t ${IMAGE_PREFIX}/barkland:${IMAGE_TAG} -f Dockerfile .

echo "Building and Pushing Sandbox Router Image..."
docker build --push -t ${IMAGE_PREFIX}/sandbox-router:${IMAGE_TAG} -f agentic-sandbox-client/sandbox-router/Dockerfile agentic-sandbox-client/sandbox-router

echo "Done."
