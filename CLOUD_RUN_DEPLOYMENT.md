# 🚀 Google Cloud Run Deployment Guide

Deploy your AI Travel Planning Platform to Google Cloud Run with a live URL!

---

## ✅ Prerequisites

- ✅ Google Cloud Platform (GCP) account
- ✅ `gcloud` CLI installed ([Install](https://cloud.google.com/sdk/docs/install))
- ✅ Docker installed locally (optional, Cloud Build handles it)
- ✅ Google Gemini API key
- ✅ Project set up in GCP Console

---

## 🎯 Deployment Steps

### Step 1: Set Up GCP Project

```bash
# Set your GCP project ID
export PROJECT_ID=your-gcp-project-id

# Set the project as default
gcloud config set project $PROJECT_ID

# Verify authentication
gcloud auth login
```

### Step 2: Enable Required APIs

```bash
# Enable Cloud Run API
gcloud services enable run.googleapis.com

# Enable Cloud Build API
gcloud services enable cloudbuild.googleapis.com

# Enable Container Registry API
gcloud services enable containerregistry.googleapis.com

# Enable Artifact Registry API (recommended)
gcloud services enable artifactregistry.googleapis.com
```

### Step 3: Configure Cloud Build Secrets

```bash
# Create a secret for Gemini API Key
echo -n "your-gemini-api-key" | gcloud secrets create GEMINI_API_KEY --data-file=-

# Grant Cloud Build service account access
gcloud secrets add-iam-policy-binding GEMINI_API_KEY \
  --member=serviceAccount:$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')@cloudbuild.gserviceaccount.com \
  --role=roles/secretmanager.secretAccessor
```

### Step 4: Deploy Using Cloud Build

**Option A: Deploy from GitHub (Recommended)**

1. Push your code to GitHub
2. Connect your repository in Cloud Console:
   - Go to **Cloud Run** → **Deploy from source**
   - Select **GitHub** as source
   - Authenticate and select your repository

3. Configure the build:
   ```yaml
   Build type: Cloud Build
   Build config file: cloudbuild.yaml
   Service name: ai-travel-platform
   ```

**Option B: Deploy Using gcloud CLI**

```bash
# Clone or navigate to your project directory
cd /path/to/PromptWars

# Deploy using Cloud Build
gcloud builds submit \
  --config=cloudbuild.yaml \
  --substitutions="_SERVICE_NAME=ai-travel-platform,_REGION=us-central1,_GEMINI_API_KEY=$(gcloud secrets versions access latest --secret=GEMINI_API_KEY)"
```

### Step 5: Monitor Deployment

```bash
# View build status
gcloud builds list --limit=10

# View build logs (replace BUILD_ID)
gcloud builds log BUILD_ID

# View Cloud Run services
gcloud run services list

# View service details
gcloud run services describe ai-travel-platform --region=us-central1
```

### Step 6: Get Your Cloud Run URL

```bash
# Get the service URL
gcloud run services describe ai-travel-platform \
  --region=us-central1 \
  --format='value(status.url)'

# Output: https://ai-travel-platform-xxxxx-uc.a.run.app
```

---

## 🌐 Access Your Application

Once deployed, visit your Cloud Run URL:

```
https://ai-travel-platform-xxxxx-uc.a.run.app
```

---

## 🔐 Making Your Service Public

By default, Cloud Run requires authentication. To make it public:

```bash
# Allow unauthenticated access
gcloud run services add-iam-policy-binding ai-travel-platform \
  --member=allUsers \
  --role=roles/run.invoker \
  --region=us-central1
```

To restrict access again:

```bash
# Remove public access
gcloud run services remove-iam-policy-binding ai-travel-platform \
  --member=allUsers \
  --role=roles/run.invoker \
  --region=us-central1
```

---

## 🛠️ Manual Deployment (Docker Build Locally)

If you prefer to build locally and push:

```bash
# Set service name
SERVICE_NAME=ai-travel-platform
REGION=us-central1

# Build Docker image
docker build -t gcr.io/$PROJECT_ID/$SERVICE_NAME:latest .

# Configure Docker auth (one-time)
gcloud auth configure-docker gcr.io

# Push to Container Registry
docker push gcr.io/$PROJECT_ID/$SERVICE_NAME:latest

# Deploy to Cloud Run
gcloud run deploy $SERVICE_NAME \
  --image=gcr.io/$PROJECT_ID/$SERVICE_NAME:latest \
  --region=$REGION \
  --platform=managed \
  --memory=512Mi \
  --cpu=1 \
  --timeout=3600 \
  --max-instances=100 \
  --allow-unauthenticated \
  --set-env-vars="GEMINI_API_KEY=your-key-here,LOG_LEVEL=INFO"
```

---

## 📊 Cloud Run Configuration

The deployment uses these Cloud Run settings:

| Setting | Value | Purpose |
|---------|-------|---------|
| **Memory** | 512MB | Sufficient for AI processing |
| **CPU** | 1 vCPU | Balanced performance |
| **Timeout** | 3600s | Long requests for AI |
| **Max Instances** | 100 | Auto-scaling capacity |
| **Concurrency** | 80 | Per-instance concurrency |
| **Authentication** | Optional | Configure per your needs |

### Custom Configuration

To modify settings:

```bash
# Update memory and CPU
gcloud run services update ai-travel-platform \
  --memory=1Gi \
  --cpu=2 \
  --region=us-central1

# Set max instances
gcloud run services update ai-travel-platform \
  --max-instances=200 \
  --region=us-central1

# Add environment variables
gcloud run services update ai-travel-platform \
  --set-env-vars="DEBUG=false,ENABLE_CACHING=true" \
  --region=us-central1
```

---

## 🔍 Monitoring & Logging

### View Logs

```bash
# Real-time logs
gcloud run services logs read ai-travel-platform --region=us-central1 --limit=50

# Tail logs
gcloud run services logs read ai-travel-platform --region=us-central1 --follow

# Advanced: View in Cloud Logging
# Go to Cloud Logging console and filter by service name
```

### Monitor Performance

```bash
# View metrics
gcloud monitoring list-time-series \
  --filter='resource.type="cloud_run_revision"'

# Use Cloud Console for dashboard
# Cloud Console → Cloud Run → Select service → Metrics
```

### Set Up Alerts

1. Go to **Monitoring** → **Alerting policies**
2. Create policy for:
   - High error rate
   - Slow response time
   - High CPU/memory usage

---

## 💰 Cost Optimization

### Reduce Costs

```bash
# Lower memory allocation
gcloud run services update ai-travel-platform \
  --memory=256Mi \
  --region=us-central1

# Set concurrent requests
gcloud run services update ai-travel-platform \
  --concurrency=50 \
  --region=us-central1

# Use startup probes for efficiency
# Configure in Cloud Run console
```

### Estimate Costs

- **Compute**: First 180,000 vCPU-seconds/month free
- **Requests**: First 2,000,000 requests/month free
- **Networking**: Free ingress, charges for egress

---

## 🧹 Cleanup

### Remove Service

```bash
# Delete Cloud Run service
gcloud run services delete ai-travel-platform \
  --region=us-central1 \
  --quiet
```

### Clean Up Images

```bash
# List images
gcloud container images list --project=$PROJECT_ID

# Delete image
gcloud container images delete gcr.io/$PROJECT_ID/ai-travel-platform:latest
```

---

## 🐛 Troubleshooting

### Port Not Responding

```bash
# Check that application listens on PORT env var
# Cloud Run sets PORT automatically (usually 8080)
# Verify in Dockerfile: CMD uses port variable
```

### High Memory Usage

```bash
# Increase memory allocation
gcloud run services update ai-travel-platform \
  --memory=1Gi \
  --region=us-central1
```

### Timeout Errors

```bash
# Increase timeout
gcloud run services update ai-travel-platform \
  --timeout=3600 \
  --region=us-central1
```

### API Key Not Working

```bash
# Verify secret is accessible
gcloud secrets versions access latest --secret=GEMINI_API_KEY

# Update environment variable
gcloud run services update ai-travel-platform \
  --set-env-vars="GEMINI_API_KEY=$(gcloud secrets versions access latest --secret=GEMINI_API_KEY)" \
  --region=us-central1
```

### Service Won't Start

```bash
# Check logs
gcloud run services logs read ai-travel-platform \
  --region=us-central1 \
  --limit=100 \
  --follow

# Redeploy with debug enabled
gcloud run deploy ai-travel-platform \
  --image=gcr.io/$PROJECT_ID/ai-travel-platform:latest \
  --set-env-vars="DEBUG=true,LOG_LEVEL=DEBUG" \
  --region=us-central1
```

---

## 🔄 CI/CD Integration

### GitHub Actions

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Cloud Run

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - uses: google-github-actions/setup-gcloud@v0
        with:
          project_id: ${{ secrets.GCP_PROJECT_ID }}
          service_account_key: ${{ secrets.GCP_SA_KEY }}

      - name: Build and deploy
        run: |
          gcloud builds submit \
            --config=cloudbuild.yaml \
            --substitutions="_GEMINI_API_KEY=${{ secrets.GEMINI_API_KEY }}"
```

### GitLab CI

Create `.gitlab-ci.yml`:

```yaml
deploy_cloud_run:
  stage: deploy
  image: google/cloud-sdk
  script:
    - gcloud auth activate-service-account --key-file=$GCP_SA_KEY
    - gcloud config set project $GCP_PROJECT_ID
    - |
      gcloud builds submit \
        --config=cloudbuild.yaml \
        --substitutions="_GEMINI_API_KEY=$GEMINI_API_KEY"
  only:
    - main
```

---

## 📱 API Usage from Cloud Run URL

Once deployed, use the cloud URL for API calls:

### Web UI Access
```
https://ai-travel-platform-xxxxx-uc.a.run.app
```

### REST API Access

```bash
# Plan a trip
curl -X POST https://ai-travel-platform-xxxxx-uc.a.run.app/api/v1/trips/plan \
  -H "Content-Type: application/json" \
  -d '{
    "destination": "Tokyo",
    "start_date": "2024-06-01",
    "end_date": "2024-06-07",
    "travelers": 2,
    "budget": 3000,
    "preferences": ["cultural", "adventure"]
  }'

# Get trip details
curl https://ai-travel-platform-xxxxx-uc.a.run.app/api/v1/trips/{trip_id}
```

---

## 🎓 Advanced Configuration

### Custom Domain

1. Go to **Cloud Run** → Select service
2. Click **Manage custom domains**
3. Follow verification steps
4. Add your custom domain

### SSL/TLS

- Automatically managed by Cloud Run
- Free HTTPS certificate included

### VPC Connector

For Firestore access:

```bash
# Create VPC connector
gcloud compute networks vpc-access connectors create cloud-run-connector \
  --region=us-central1 \
  --subnet=default \
  --min-instances=2 \
  --max-instances=10

# Use in deployment
gcloud run deploy ai-travel-platform \
  --vpc-connector=cloud-run-connector \
  --region=us-central1
```

---

## 📚 Additional Resources

- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Deploying from Source](https://cloud.google.com/run/docs/deploying-source-code)
- [Cloud Run Pricing](https://cloud.google.com/run/pricing)
- [Cloud Build Configuration](https://cloud.google.com/build/docs/build-config-file-schema)

---

## ✅ Deployment Checklist

- [ ] GCP project created
- [ ] APIs enabled
- [ ] Gemini API key configured
- [ ] Cloud Build secrets set up
- [ ] Code committed to repository
- [ ] cloudbuild.yaml configured
- [ ] Cloud Run service deployed
- [ ] Service URL verified
- [ ] Web UI accessible
- [ ] API endpoints working
- [ ] Monitoring configured
- [ ] Alerts set up
- [ ] Cost tracking enabled

---

**Your AI Travel Platform is now LIVE on Cloud Run!** 🎉

**Share your Cloud Run URL:** `https://ai-travel-platform-xxxxx-uc.a.run.app`
