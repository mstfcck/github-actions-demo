"""
Azure OpenAI Provider Implementation.
Concrete implementation of AIProvider interface.
"""

import asyncio
import json
import os
from typing import Dict, Any
from openai import AsyncAzureOpenAI
from ..interfaces.ai_provider import AIProvider, AIProviderError
from ..models.pr_data import PullRequestData
from ..models.review_result import ReviewResult, ReviewComment, ReviewSeverity
from ..utils.logger import get_logger


class AzureOpenAIProvider(AIProvider):
    """
    Azure OpenAI implementation of AIProvider.
    
    SOLID Principles Applied:
    - Single Responsibility: Only handles Azure OpenAI interactions
    - Open/Closed: Implements interface without modifying it
    - Liskov Substitution: Can replace any AIProvider
    - Dependency Inversion: Depends on AIProvider abstraction
    """
    
    def __init__(self):
        """Initialize Azure OpenAI client with environment variables."""
        self.logger = get_logger(__name__)
        
        # Get Azure OpenAI configuration from environment
        self.endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4")
        
        if not all([self.endpoint, self.api_key]):
            raise AIProviderError(
                "Missing required Azure OpenAI configuration", 
                "azure_openai"
            )
        
        # Initialize Azure OpenAI client
        self.client = AsyncAzureOpenAI(
            azure_endpoint=self.endpoint,
            api_key=self.api_key,
            api_version="2024-02-15-preview"
        )
        
        self.logger.info("Azure OpenAI provider initialized")
    
    async def analyze_pull_request(
        self, 
        pr_data: PullRequestData, 
        config: Dict[str, Any]
    ) -> ReviewResult:
        """
        Analyze pull request using Azure OpenAI.
        
        Following Azure best practices:
        - Proper error handling with exponential backoff
        - Secure credential handling
        - Logging for monitoring
        """
        try:
            self.logger.info(f"Analyzing PR #{pr_data.number}: {pr_data.title}")
            
            # Prepare analysis prompt
            prompt = self._create_analysis_prompt(pr_data)
            
            # Call Azure OpenAI with retry logic
            response = await self._call_azure_openai_with_retry(prompt, config)
            
            # Parse and return results
            return self._parse_response(response)
            
        except Exception as e:
            self.logger.error(f"Error analyzing PR: {e}")
            raise AIProviderError(f"Analysis failed: {e}", "azure_openai")
    
    def _create_analysis_prompt(self, pr_data: PullRequestData) -> str:
        """Create analysis prompt from PR data."""
        files_info = []
        for file_change in pr_data.files_changed[:5]:  # Limit to first 5 files
            files_info.append({
                "filename": file_change.filename,
                "status": file_change.status,
                "changes": f"+{file_change.additions}/-{file_change.deletions}",
                "patch": file_change.patch[:1000] if file_change.patch else None  # Truncate
            })
        
        return f"""
        You are a senior code reviewer. Analyze this pull request and provide feedback.
        
        PR Title: {pr_data.title}
        Description: {pr_data.body[:500]}  # Truncate description
        Author: {pr_data.author}
        Files changed: {len(pr_data.files_changed)}
        Total changes: {pr_data.get_total_changes()} lines
        
        File Changes:
        {json.dumps(files_info, indent=2)}
        
        Provide your review in this JSON format:
        {{
            "summary": "Brief overall assessment",
            "comments": [
                {{
                    "filename": "file.py or null",
                    "line_number": 123 or null,
                    "message": "Specific feedback",
                    "severity": "info|warning|error"
                }}
            ],
            "overall_score": 7,
            "approved": true
        }}
        
        Focus on: code quality, best practices, potential bugs, security issues.
        Keep comments constructive and specific.
        """
    
    async def _call_azure_openai_with_retry(
        self, 
        prompt: str, 
        config: Dict[str, Any],
        max_retries: int = 3
    ) -> str:
        """Call Azure OpenAI with exponential backoff retry logic."""
        last_exception = None
        
        for attempt in range(max_retries):
            try:
                response = await self.client.chat.completions.create(
                    model=self.deployment_name,
                    messages=[
                        {"role": "system", "content": "You are a helpful code reviewer."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=config.get("max_tokens", 1500),
                    temperature=config.get("temperature", 0.1)
                )
                
                return response.choices[0].message.content or ""
                
            except Exception as e:
                last_exception = e
                if attempt == max_retries - 1:
                    break
                
                # Exponential backoff
                wait_time = 2 ** attempt
                self.logger.warning(f"Retry {attempt + 1} after {wait_time}s: {e}")
                await asyncio.sleep(wait_time)
        
        # If we get here, all retries failed
        raise AIProviderError(f"All retries failed: {last_exception}", "azure_openai")
    
    def _parse_response(self, response: str) -> ReviewResult:
        """Parse Azure OpenAI response into ReviewResult."""
        try:
            # Extract JSON from response
            data = json.loads(response)
            
            # Convert comments
            comments = []
            for comment_data in data.get("comments", []):
                comment = ReviewComment(
                    filename=comment_data.get("filename"),
                    line_number=comment_data.get("line_number"),
                    message=comment_data["message"],
                    severity=ReviewSeverity(comment_data.get("severity", "info"))
                )
                comments.append(comment)
            
            return ReviewResult(
                summary=data["summary"],
                comments=comments,
                overall_score=data.get("overall_score", 5),
                approved=data.get("approved", True)
            )
            
        except (json.JSONDecodeError, KeyError) as e:
            self.logger.error(f"Failed to parse response: {e}")
            # Fallback result
            return ReviewResult(
                summary="Analysis completed but response format was invalid",
                comments=[],
                overall_score=5,
                approved=True
            )
