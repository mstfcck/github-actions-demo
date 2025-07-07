#!/bin/bash

# Local test script for the Azure OpenAI PR Review Agent
echo "🚀 Testing Azure OpenAI PR Review Agent locally..."

# Set test environment variables
export AZURE_OPENAI_ENDPOINT="your-endpoint-here"
export AZURE_OPENAI_API_KEY="your-key-here"
export AZURE_OPENAI_DEPLOYMENT_NAME="gpt-4"
export GITHUB_PR_NUMBER="123"
export GITHUB_PR_TITLE="Test PR for AI Review"
export GITHUB_PR_BODY="This is a test PR to validate our AI review agent"
export GITHUB_ACTOR="testuser"
export LOG_LEVEL="INFO"

echo "Building Docker image..."
docker build -t pr-review-agent .

echo "Running Docker container..."
docker run --rm \
  -e AZURE_OPENAI_ENDPOINT="$AZURE_OPENAI_ENDPOINT" \
  -e AZURE_OPENAI_API_KEY="$AZURE_OPENAI_API_KEY" \
  -e AZURE_OPENAI_DEPLOYMENT_NAME="$AZURE_OPENAI_DEPLOYMENT_NAME" \
  -e GITHUB_PR_NUMBER="$GITHUB_PR_NUMBER" \
  -e GITHUB_PR_TITLE="$GITHUB_PR_TITLE" \
  -e GITHUB_PR_BODY="$GITHUB_PR_BODY" \
  -e GITHUB_ACTOR="$GITHUB_ACTOR" \
  -e LOG_LEVEL="$LOG_LEVEL" \
  pr-review-agent

echo "✅ Local test completed!"
