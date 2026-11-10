#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
project=whatevercooker
region=us-central1
image="$region-docker.pkg.dev/$project/website/site:$(date -u +%Y%m%d%H%M%S)"
gcloud builds submit --project="$project" --tag="$image" .
gcloud run deploy whatevercooker --project="$project" --region="$region" \
  --image="$image" --port=8080 --allow-unauthenticated \
  --service-account="website-runtime@$project.iam.gserviceaccount.com" \
  --cpu=1 --memory=256Mi --min-instances=0 --max-instances=3 \
  --concurrency=80 --timeout=30 --quiet
