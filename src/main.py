"""
Main entry point for the Azure OpenAI PR Review Agent.

ARCHITECTURE OVERVIEW:
======================
This GitHub Action follows a clean architecture pattern with SOLID principles:

1. TRIGGER: GitHub PR events (opened/synchronize/reopened) start the workflow
2. DOCKER: GitHub Actions runs this Python app in a Docker container
3. ENVIRONMENT: Azure OpenAI credentials are passed via environment variables
4. EXTRACTION: PR data is extracted from GitHub Actions context
5. ANALYSIS: Azure OpenAI analyzes the code changes and provides feedback
6. OUTPUT: Results are formatted for GitHub Actions outputs and PR comments

FLOW:
=====
GitHub PR Event → GitHub Actions Workflow → Docker Container → Python App →
Azure OpenAI API → AI Analysis → Structured Results → GitHub PR Comment

SOLID PRINCIPLES:
================
- Single Responsibility: Each class has one clear purpose
- Open/Closed: New AI providers can be added without modifying existing code
- Liskov Substitution: Any AIProvider implementation can replace AzureOpenAIProvider
- Interface Segregation: Clean interfaces for AI providers
- Dependency Inversion: High-level modules depend on abstractions, not concretions

ENVIRONMENT VARIABLES READ:
==========================
This application reads the following environment variables set by GitHub Actions:

AZURE OPENAI CONFIGURATION (from repository secrets):
• AZURE_OPENAI_ENDPOINT: Azure OpenAI service endpoint URL
• AZURE_OPENAI_API_KEY: Authentication key for Azure OpenAI API
• AZURE_OPENAI_DEPLOYMENT_NAME: Model deployment name (e.g., "gpt-4")

AI MODEL PARAMETERS (from action inputs):
• MAX_TOKENS: Maximum response length (default: 1500)
• TEMPERATURE: AI creativity setting 0.0-1.0 (default: 0.1)

GITHUB CONTEXT (automatically provided by GitHub Actions):
• GITHUB_EVENT_PATH: Path to webhook event payload JSON
• GITHUB_TOKEN: Token for GitHub API authentication
• GITHUB_REPOSITORY: Repository name (owner/repo format)
• GITHUB_ACTOR: User who triggered the workflow
• GITHUB_SHA: Commit SHA being built
• GITHUB_REF: Git ref (branch/tag) being built
• GITHUB_OUTPUT: File path for setting action outputs

EXECUTION PHASES:
================
1. INITIALIZATION: Set up logging, read environment variables
2. DATA EXTRACTION: Get PR information from GitHub context
3. SERVICE SETUP: Initialize AI provider and review service (dependency injection)
4. AI ANALYSIS: Send code to Azure OpenAI for analysis
5. RESULT PROCESSING: Parse AI response into structured format
6. OUTPUT GENERATION: Create GitHub Actions outputs for workflow consumption

Demonstrates SOLID principles and clean architecture.
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from typing import List

from .providers.azure_openai_provider import AzureOpenAIProvider
from .services.pr_review_service import PRReviewService
from .models.pr_data import PullRequestData, FileChange
from .utils.logger import get_logger


async def main():
    """
    Main function - orchestrates the review process.
    
    GITHUB ACTIONS INTEGRATION:
    ===========================
    This function is the entry point when GitHub Actions runs the Docker container.
    It coordinates the entire PR review process:
    
    1. Extract PR data from GitHub Actions environment variables
    2. Initialize Azure OpenAI provider with credentials from secrets
    3. Create review service with dependency injection
    4. Perform AI-powered analysis of the PR
    5. Output results in GitHub Actions format for workflow consumption
    
    ENVIRONMENT VARIABLES USED:
    ==========================
    AZURE OPENAI CONFIGURATION:
    • AZURE_OPENAI_ENDPOINT: Azure OpenAI service endpoint
    • AZURE_OPENAI_API_KEY: Authentication key for Azure OpenAI
    • AZURE_OPENAI_DEPLOYMENT_NAME: Model deployment name (e.g., "gpt-4")
    
    AI MODEL PARAMETERS:
    • MAX_TOKENS: Maximum tokens for AI response
    • TEMPERATURE: AI creativity/randomness setting (0.0-1.0)
    
    GITHUB CONTEXT VARIABLES:
    • GITHUB_EVENT_PATH: Path to PR webhook payload JSON file
    • GITHUB_TOKEN: GitHub API authentication token
    • GITHUB_REPOSITORY: Repository name (owner/repo)
    • GITHUB_ACTOR: User who triggered the workflow
    • GITHUB_OUTPUT: File path for setting GitHub Actions outputs
    
    ERROR HANDLING STRATEGY:
    =======================
    • Comprehensive logging for debugging workflow issues
    • Graceful degradation if Azure OpenAI is unavailable
    • Proper exit codes for GitHub Actions status indication
    • Structured error messages for troubleshooting
    
    OUTPUTS GENERATED:
    =================
    The function generates outputs consumable by GitHub Actions workflows:
    • summary: Brief text summary of the review
    • score: Numerical score (1-10) representing code quality
    • approved: Boolean indicating if the PR should be approved
    • comment_count: Number of specific review comments
    • review_result: Complete structured JSON with all review data
    
    Demonstrates:
    - Dependency Injection (SOLID: Dependency Inversion)
    - Error handling and logging
    - Clean separation of concerns
    """
    logger = get_logger(__name__)
    
    try:
        logger.info("Starting Azure OpenAI PR Review Agent")
        logger.info("Environment: GitHub Actions Docker Container")
        
        # ===================================================================
        # PHASE 1: EXTRACT PR DATA FROM GITHUB ACTIONS ENVIRONMENT
        # ===================================================================
        # Get PR data from GitHub Actions context
        # NOTE: In real implementation, this should use GitHub API to fetch actual PR data
        # from the GitHub Actions context (GITHUB_EVENT_PATH, GITHUB_TOKEN, etc.)
        logger.info("Phase 1: Extracting PR data from GitHub Actions environment")
        pr_data = _get_pr_data_from_github()
        logger.info(f"Extracted PR #{pr_data.number}: '{pr_data.title}' by {pr_data.author}")
        logger.info(f"Files changed: {len(pr_data.files_changed)}, Total changes: {pr_data.get_total_changes()} lines")
        
        # ===================================================================
        # PHASE 2: INITIALIZE AI PROVIDER WITH DEPENDENCY INJECTION
        # ===================================================================
        # Initialize AI provider (Dependency Injection)
        # The provider reads Azure OpenAI credentials from environment variables
        # set by the GitHub Actions workflow from repository secrets
        logger.info("Phase 2: Initializing Azure OpenAI provider")
        ai_provider = AzureOpenAIProvider()
        logger.info("Azure OpenAI provider initialized successfully")
        
        # ===================================================================
        # PHASE 3: CREATE REVIEW SERVICE WITH INJECTED DEPENDENCIES
        # ===================================================================
        # Initialize review service with injected AI provider
        # This demonstrates SOLID's Dependency Inversion Principle
        logger.info("Phase 3: Creating PR review service")
        review_service = PRReviewService(ai_provider)
        logger.info("Review service created with dependency injection")
        
        # ===================================================================
        # PHASE 4: PERFORM AI-POWERED ANALYSIS
        # ===================================================================
        # Perform review - this calls Azure OpenAI API to analyze the PR
        logger.info("Phase 4: Starting AI-powered PR analysis")
        result = await review_service.review_pull_request(pr_data)
        logger.info(f"AI analysis completed - Score: {result.overall_score}/10, Approved: {result.approved}")
        logger.info(f"Generated {len(result.comments)} specific comments")
        
        # ===================================================================
        # PHASE 5: OUTPUT RESULTS FOR GITHUB ACTIONS CONSUMPTION
        # ===================================================================
        # Output results for GitHub Actions consumption
        # This sets GitHub Actions outputs that can be used by subsequent workflow steps
        logger.info("Phase 5: Generating GitHub Actions outputs")
        _output_results(result)
        logger.info("GitHub Actions outputs generated successfully")
        
        logger.info("Review completed successfully - all phases complete")
        
    except Exception as e:
        # Comprehensive error logging for debugging
        logger.error(f"Review failed in main orchestration: {e}")
        logger.error(f"Error type: {type(e).__name__}")
        logger.error("Check Azure OpenAI credentials and GitHub Actions environment")
        
        # Exit with error code to signal failure to GitHub Actions
        sys.exit(1)


def _get_pr_data_from_github() -> PullRequestData:
    """
    Extract PR data from GitHub Actions environment.
    
    GITHUB ACTIONS CONTEXT:
    =======================
    In a real implementation, this function should:
    
    1. Read GITHUB_EVENT_PATH file to get the PR webhook payload
    2. Use GITHUB_TOKEN to authenticate with GitHub API
    3. Extract PR details: number, title, body, author, branches
    4. Fetch file changes using GitHub API
    5. Get diff/patch data for each changed file
    
    CURRENT IMPLEMENTATION:
    ======================
    For demonstration purposes, this creates sample data.
    The sample shows the expected data structure that the AI provider needs.
    
    ENVIRONMENT VARIABLES AVAILABLE:
    ===============================
    - GITHUB_EVENT_PATH: Path to webhook event payload JSON
    - GITHUB_TOKEN: Token for GitHub API authentication  
    - GITHUB_REPOSITORY: Repository name (owner/repo)
    - GITHUB_ACTOR: User who triggered the workflow
    - GITHUB_SHA: Commit SHA being built
    - GITHUB_REF: Git ref (branch/tag) being built
    
    In a real implementation, this would use GitHub API.
    For now, we'll create sample data for demonstration.
    """
    # In real implementation, get from GitHub API using:
    # - GITHUB_TOKEN
    # - GITHUB_REPOSITORY
    # - GITHUB_EVENT_PATH
    
    # Sample data for demonstration
    sample_files = [
        FileChange(
            filename="src/main.py",
            status="modified",
            additions=15,
            deletions=3,
            patch="@@ -10,7 +10,19 @@ def main():\\n+    # Added error handling\\n+    try:\\n+        result = process()\\n+    except Exception as e:\\n+        logger.error(f'Error: {e}')\\n+        return 1"
        ),
        FileChange(
            filename="README.md",
            status="modified",
            additions=5,
            deletions=1,
            patch="@@ -1,4 +1,8 @@ # Project\\n+\\n+## New Section\\n+\\nAdded documentation for new features."
        )
    ]
    
    return PullRequestData(
        number=int(os.getenv("GITHUB_PR_NUMBER", "123")),
        title=os.getenv("GITHUB_PR_TITLE", "Add error handling and documentation"),
        body=os.getenv("GITHUB_PR_BODY", "This PR adds error handling to the main function and updates documentation."),
        author=os.getenv("GITHUB_ACTOR", "developer"),
        base_branch="main",
        head_branch="feature/error-handling",
        files_changed=sample_files
    )


def _output_results(result):
    """
    Output review results for GitHub Actions consumption.
    
    GITHUB ACTIONS OUTPUTS:
    =======================
    This function creates outputs that GitHub Actions can use:
    
    1. INDIVIDUAL OUTPUTS: Set specific values (summary, score, approved, etc.)
       - These can be referenced in subsequent workflow steps
       - Example: steps.review.outputs.score
    
    2. JSON OUTPUT: Complete review result as structured data
       - Used by the workflow to create formatted PR comments
       - Contains all review details in machine-readable format
    
    3. LOGGING: Detailed review information for workflow debugging
    
    OUTPUT METHODS:
    ==============
    - Modern: Write to $GITHUB_OUTPUT file (GitHub Actions recommended)
    - Fallback: Print to stdout for local testing
    
    WORKFLOW INTEGRATION:
    ====================
    The GitHub Actions workflow (pr-review.yml) uses these outputs to:
    - Create formatted comments on the PR
    - Provide fallback comments if something fails
    - Allow conditional logic based on review results
    
    Args:
        result: ReviewResult to output
    """
    logger = get_logger(__name__)
    
    # Create GitHub Actions outputs for workflow consumption
    # These individual outputs can be referenced in subsequent workflow steps
    outputs = {
        "summary": result.summary,           # Brief review summary
        "score": result.overall_score,       # Numeric score (1-10)
        "approved": result.approved,         # Boolean approval status
        "comment_count": len(result.comments) # Number of specific comments
    }
    
    # Create JSON result for detailed workflow consumption
    # This contains the complete review data in structured format
    result_json = {
        "summary": result.summary,
        "overall_score": result.overall_score,
        "approved": result.approved,
        "comments": [
            {
                "filename": c.filename,
                "line_number": c.line_number,
                "message": c.message,
                "severity": c.severity.value
            }
            for c in result.comments
        ]
    }
    
    # Set GitHub Actions outputs using the modern method
    # This writes to the $GITHUB_OUTPUT file that GitHub Actions reads
    github_output = os.getenv("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a") as f:
            # Write individual outputs for easy access in workflow
            for key, value in outputs.items():
                f.write(f"{key}={value}\n")
            # Write complete JSON result for complex processing
            f.write(f"review_result={json.dumps(result_json)}\n")
    else:
        # Fallback for local testing when $GITHUB_OUTPUT is not available
        for key, value in outputs.items():
            print(f"{key}={value}")
        print(f"review_result={json.dumps(result_json)}")
    
    # Create formatted review comment for debugging/logging
    # This shows what the final PR comment will look like
    comment_body = _format_review_comment(result)
    
    # Log the review comment
    logger.info("Review comment:")
    logger.info(comment_body)


def _format_review_comment(result) -> str:
    """Format review result as GitHub comment."""
    lines = [
        "## 🤖 AI Code Review",
        "",
        f"**Overall Score:** {result.overall_score}/10",
        f"**Status:** {'✅ Approved' if result.approved else '❌ Changes Requested'}",
        "",
        "### Summary",
        result.summary,
        ""
    ]
    
    if result.comments:
        lines.extend([
            "### Comments",
            ""
        ])
        
        for comment in result.comments:
            emoji = {"info": "ℹ️", "warning": "⚠️", "error": "❌"}
            severity_emoji = emoji.get(comment.severity.value, "ℹ️")
            
            if comment.filename and comment.line_number:
                lines.append(f"{severity_emoji} **{comment.filename}:{comment.line_number}**")
            elif comment.filename:
                lines.append(f"{severity_emoji} **{comment.filename}**")
            else:
                lines.append(f"{severity_emoji} **General**")
            
            lines.append(f"  {comment.message}")
            lines.append("")
    
    lines.append("---")
    lines.append("*Generated by Azure OpenAI PR Review Agent*")
    
    return "\\n".join(lines)


if __name__ == "__main__":
    asyncio.run(main())
