"""
Main entry point for the Azure OpenAI PR Review Agent.
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
    
    Demonstrates:
    - Dependency Injection (SOLID: Dependency Inversion)
    - Error handling and logging
    - Clean separation of concerns
    """
    logger = get_logger(__name__)
    
    try:
        logger.info("Starting Azure OpenAI PR Review Agent")
        
        # Get PR data from GitHub Actions environment
        pr_data = _get_pr_data_from_github()
        
        # Initialize AI provider (Dependency Injection)
        ai_provider = AzureOpenAIProvider()
        
        # Initialize review service
        review_service = PRReviewService(ai_provider)
        
        # Perform review
        result = await review_service.review_pull_request(pr_data)
        
        # Output results for GitHub Actions
        _output_results(result)
        
        logger.info("Review completed successfully")
        
    except Exception as e:
        logger.error(f"Review failed: {e}")
        sys.exit(1)


def _get_pr_data_from_github() -> PullRequestData:
    """
    Extract PR data from GitHub Actions environment.
    
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
    Output review results for GitHub Actions.
    
    Args:
        result: ReviewResult to output
    """
    logger = get_logger(__name__)
    
    # Create GitHub Actions outputs
    outputs = {
        "summary": result.summary,
        "score": result.overall_score,
        "approved": result.approved,
        "comment_count": len(result.comments)
    }
    
    # Create JSON result for detailed output
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
    
    # Set GitHub Actions outputs (new method)
    github_output = os.getenv("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a") as f:
            for key, value in outputs.items():
                f.write(f"{key}={value}\n")
            # Add the JSON result
            f.write(f"review_result={json.dumps(result_json)}\n")
    else:
        # Fallback for local testing
        for key, value in outputs.items():
            print(f"{key}={value}")
        print(f"review_result={json.dumps(result_json)}")
    
    # Create review comment for PR
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
