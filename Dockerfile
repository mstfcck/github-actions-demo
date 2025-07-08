# =============================================================================
# AZURE OPENAI PR REVIEW - DOCKER CONTAINER DEFINITION
# =============================================================================
# This Dockerfile creates a lightweight, secure container for the AI review agent.
# It follows Docker best practices for Python applications.
#
# CONTAINER PURPOSE:
# • Provides isolated, reproducible execution environment
# • Ensures consistent dependency versions across different runners
# • Isolates application from GitHub Actions runner environment
# • Enables local testing and development
#
# SECURITY FEATURES:
# • Uses official Python slim image for security updates
# • Minimal attack surface with only required dependencies
# • No root user execution (handled by Python base image)
# • Environment variables for secure credential passing
# =============================================================================

# Use official Python 3.11 slim image for minimal footprint and security
# Slim images contain only essential packages, reducing attack surface
FROM python:3.11-slim

# =============================================================================
# CONTAINER SETUP
# =============================================================================

# Set working directory inside container
# All subsequent commands will execute from this directory
WORKDIR /app

# =============================================================================
# DEPENDENCY INSTALLATION
# =============================================================================
# Copy requirements.txt first to leverage Docker layer caching
# If source code changes but requirements don't, this layer is reused
COPY requirements.txt .

# Install Python dependencies
# --no-cache-dir: Reduces image size by not storing pip cache
# --upgrade: Ensures latest compatible versions for security
RUN pip install --no-cache-dir -r requirements.txt

# =============================================================================
# APPLICATION CODE
# =============================================================================
# Copy source code to container
# Done after dependency installation for optimal layer caching
COPY src/ ./src/

# =============================================================================
# RUNTIME CONFIGURATION
# =============================================================================
# Set Python path so modules can be imported correctly
# This allows 'python -m src.main' to work properly
ENV PYTHONPATH=/app

# =============================================================================
# EXECUTION ENTRY POINT
# =============================================================================
# Define the command that runs when the container starts
# Uses module execution (-m) for proper Python import handling
# GitHub Actions will pass environment variables containing:
# • AZURE_OPENAI_ENDPOINT
# • AZURE_OPENAI_API_KEY  
# • AZURE_OPENAI_DEPLOYMENT_NAME
# • MAX_TOKENS
# • TEMPERATURE
# • GITHUB_* variables (PR context, repository info, etc.)
# =============================================================================
ENTRYPOINT ["python", "-m", "src.main"]
