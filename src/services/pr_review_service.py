"""
PR Review Service - Single Responsibility Principle.
Orchestrates the PR review process.
"""

import os
from typing import Dict, Any
from ..interfaces.ai_provider import AIProvider
from ..models.pr_data import PullRequestData
from ..models.review_result import ReviewResult
from ..utils.logger import get_logger


class PRReviewService:
    """
    Service for orchestrating pull request reviews.
    
    SOLID Principles Applied:
    - Single Responsibility: Only handles PR review orchestration
    - Dependency Inversion: Depends on AIProvider abstraction
    - Open/Closed: Open for extension with new features
    """
    
    def __init__(self, ai_provider: AIProvider):
        """
        Initialize with AI provider dependency injection.
        
        Args:
            ai_provider: AI provider implementation (Dependency Inversion)
        """
        self.ai_provider = ai_provider
        self.logger = get_logger(__name__)
        
        # Load configuration from environment
        self.config = self._load_config()
    
    async def review_pull_request(self, pr_data: PullRequestData) -> ReviewResult:
        """
        Review a pull request using the configured AI provider.
        
        Args:
            pr_data: Pull request data to review
            
        Returns:
            ReviewResult: Analysis results and recommendations
        """
        self.logger.info(f"Starting review for PR #{pr_data.number}")
        
        try:
            # Validate PR data
            self._validate_pr_data(pr_data)
            
            # Perform analysis using AI provider
            result = await self.ai_provider.analyze_pull_request(pr_data, self.config)
            
            self.logger.info(f"Review completed for PR #{pr_data.number}")
            return result
            
        except Exception as e:
            self.logger.error(f"Review failed for PR #{pr_data.number}: {e}")
            raise
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from environment variables."""
        return {
            "max_tokens": int(os.getenv("MAX_TOKENS", "1500")),
            "temperature": float(os.getenv("TEMPERATURE", "0.1")),
            "max_files": int(os.getenv("MAX_FILES", "10")),
            "max_patch_size": int(os.getenv("MAX_PATCH_SIZE", "1000"))
        }
    
    def _validate_pr_data(self, pr_data: PullRequestData) -> None:
        """
        Validate PR data before processing.
        
        Args:
            pr_data: Pull request data to validate
            
        Raises:
            ValueError: If PR data is invalid
        """
        if not pr_data.title.strip():
            raise ValueError("PR title cannot be empty")
        
        if not pr_data.files_changed:
            raise ValueError("PR must have at least one file change")
        
        if pr_data.get_total_changes() == 0:
            raise ValueError("PR must have actual code changes")
        
        self.logger.debug(f"PR data validation passed for #{pr_data.number}")
