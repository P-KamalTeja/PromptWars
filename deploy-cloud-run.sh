#!/bin/bash

# Deploy AI Travel Platform to Google Cloud Run
# Usage: ./deploy-cloud-run.sh [project-id] [gemini-api-key]

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'  # No Color

# Default values
SERVICE_NAME="ai-travel-platform"
REGION="us-central1"
MEMORY="512Mi"
CPU="1"
TIMEOUT="3600"
MAX_INSTANCES="100"

# Print colored output
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    print_info "Checking prerequisites..."

    if ! command -v gcloud &> /dev/null; then
        print_error "gcloud CLI not found. Please install: https://cloud.google.com/sdk/docs/install"
        exit 1
    fi

    if ! command -v git &> /dev/null; then
        print_warning "git not found. You may need it for Cloud Build."
    fi

    print_success "Prerequisites check passed"
}

# Get project ID from user or parameter
get_project_id() {
    if [ -z "$1" ]; then
        print_info "No project ID provided. Using current gcloud project..."
        PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
        
        if [ -z "$PROJECT_ID" ]; then
            print_error "No GCP project configured. Please provide project ID:"
            echo -n "Enter GCP Project ID: "
            read PROJECT_ID
        fi
    else
        PROJECT_ID="$1"
        gcloud config set project "$PROJECT_ID"
    fi

    print_success "Using project: $PROJECT_ID"
}

# Get Gemini API key
get_api_key() {
    if [ -z "$1" ]; then
        print_warning "No Gemini API key provided via parameter."
        echo -n "Enter your Gemini API Key (or press Enter to use existing secret): "
        read -s GEMINI_API_KEY
        echo ""
        
        if [ -z "$GEMINI_API_KEY" ]; then
            print_info "Will use existing GEMINI_API_KEY secret from Cloud Secrets Manager"
        fi
    else
        GEMINI_API_KEY="$1"
    fi
}

# Enable required APIs
enable_apis() {
    print_info "Enabling required Google Cloud APIs..."

    apis=(
        "run.googleapis.com"
        "cloudbuild.googleapis.com"
        "containerregistry.googleapis.com"
        "artifactregistry.googleapis.com"
    )

    for api in "${apis[@]}"; do
        print_info "Enabling $api..."
        gcloud services enable "$api" --project="$PROJECT_ID" 2>/dev/null || true
    done

    print_success "APIs enabled"
}

# Create or update secret
setup_secret() {
    if [ -n "$GEMINI_API_KEY" ]; then
        print_info "Setting up Gemini API key secret..."

        # Check if secret exists
        if gcloud secrets describe GEMINI_API_KEY --project="$PROJECT_ID" &>/dev/null; then
            print_info "Updating existing GEMINI_API_KEY secret..."
            echo -n "$GEMINI_API_KEY" | gcloud secrets versions add GEMINI_API_KEY \
                --data-file=- \
                --project="$PROJECT_ID"
        else
            print_info "Creating GEMINI_API_KEY secret..."
            echo -n "$GEMINI_API_KEY" | gcloud secrets create GEMINI_API_KEY \
                --data-file=- \
                --project="$PROJECT_ID"
        fi

        # Grant Cloud Build service account access
        SA_EMAIL=$(gcloud projects describe "$PROJECT_ID" \
            --format='value(projectNumber)')@cloudbuild.gserviceaccount.com

        gcloud secrets add-iam-policy-binding GEMINI_API_KEY \
            --member="serviceAccount:$SA_EMAIL" \
            --role=roles/secretmanager.secretAccessor \
            --project="$PROJECT_ID" \
            2>/dev/null || true

        print_success "Secret configured"
    else
        print_info "Using existing GEMINI_API_KEY secret"
    fi
}

# Build and deploy using Cloud Build
deploy_with_cloud_build() {
    print_info "Deploying using Cloud Build..."

    # Get the API key for substitution (if provided)
    if [ -n "$GEMINI_API_KEY" ]; then
        API_KEY_SUBSTITUTION="$GEMINI_API_KEY"
    else
        # Use the secret version
        API_KEY_SUBSTITUTION=$(gcloud secrets versions access latest \
            --secret=GEMINI_API_KEY \
            --project="$PROJECT_ID" 2>/dev/null || echo "")
    fi

    print_info "Starting Cloud Build..."
    gcloud builds submit \
        --config=cloudbuild.yaml \
        --substitutions="_SERVICE_NAME=$SERVICE_NAME,_REGION=$REGION,_GEMINI_API_KEY=$API_KEY_SUBSTITUTION" \
        --project="$PROJECT_ID"

    print_success "Cloud Build deployment initiated"
}

# Get Cloud Run URL
get_service_url() {
    print_info "Retrieving Cloud Run service URL..."

    SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" \
        --region="$REGION" \
        --format='value(status.url)' \
        --project="$PROJECT_ID" 2>/dev/null || echo "")

    if [ -n "$SERVICE_URL" ]; then
        print_success "Service deployed at: $SERVICE_URL"
        return 0
    else
        print_warning "Service not yet fully deployed. Check status with:"
        echo "  gcloud run services describe $SERVICE_NAME --region=$REGION --project=$PROJECT_ID"
        return 1
    fi
}

# Make service public (optional)
make_public() {
    echo ""
    print_info "Do you want to make this service publicly accessible? (y/n)"
    read -r response
    
    if [[ "$response" =~ ^[Yy]$ ]]; then
        print_info "Making service public..."
        gcloud run services add-iam-policy-binding "$SERVICE_NAME" \
            --member=allUsers \
            --role=roles/run.invoker \
            --region="$REGION" \
            --project="$PROJECT_ID" \
            --quiet

        print_success "Service is now publicly accessible"
    else
        print_info "Service remains private. Use Cloud IAM to grant access."
    fi
}

# Show deployment summary
show_summary() {
    echo ""
    print_success "═══════════════════════════════════════════════════"
    print_success "✨ Deployment Summary"
    print_success "═══════════════════════════════════════════════════"
    echo "Service Name:    $SERVICE_NAME"
    echo "Project ID:      $PROJECT_ID"
    echo "Region:          $REGION"
    echo "Memory:          $MEMORY"
    echo "CPU:             $CPU"
    echo "Timeout:         ${TIMEOUT}s"
    echo "Max Instances:   $MAX_INSTANCES"
    echo ""
    
    if [ -n "$SERVICE_URL" ]; then
        echo "🌐 Access URL: $SERVICE_URL"
    fi
    
    echo ""
    echo "📝 Useful Commands:"
    echo "  View logs:     gcloud run services logs read $SERVICE_NAME --region=$REGION --follow"
    echo "  View status:   gcloud run services describe $SERVICE_NAME --region=$REGION"
    echo "  Update env:    gcloud run services update $SERVICE_NAME --region=$REGION --set-env-vars=KEY=VALUE"
    echo "  Delete:        gcloud run services delete $SERVICE_NAME --region=$REGION"
    echo ""
    print_success "═══════════════════════════════════════════════════"
}

# Main deployment flow
main() {
    echo ""
    print_info "🚀 AI Travel Platform - Cloud Run Deployment"
    echo ""

    # Parse arguments
    PROJECT_ID="${1:-}"
    GEMINI_API_KEY="${2:-}"

    # Run deployment steps
    check_prerequisites
    get_project_id "$PROJECT_ID"
    get_api_key "$GEMINI_API_KEY"
    enable_apis
    setup_secret
    deploy_with_cloud_build
    
    # Wait a moment for service to appear
    print_info "Waiting for service to be available..."
    sleep 10
    
    get_service_url
    make_public
    show_summary

    echo ""
    print_success "Deployment process initiated! 🎉"
    echo "Your service may take a few moments to fully initialize."
    echo "Check the Cloud Run console for real-time status updates."
}

# Run main function
main "$@"
