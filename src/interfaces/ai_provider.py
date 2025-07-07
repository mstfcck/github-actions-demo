"""
AI Provider Interface - Dependency Inversion Principle.
Abstract interface that high-level modules depend on.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ..models.pr_data import PullRequestData
    from ..models.review_result import ReviewResult


class AIProvider(ABC):
    """
    Abstract AI provider interface.
    
    SOLID Principles Applied:
    - Single Responsibility: Defines contract for AI interactions only
    - Open/Closed: Open for extension with new providers
    - Dependency Inversion: High-level modules depend on this abstraction
    """
    
    @abstractmethod
    async def analyze_pull_request(
        self, 
        pr_data: "PullRequestData", 
        config: Dict[str, Any]
    ) -> "ReviewResult":
        """
        Analyze a pull request and return review results.
        
        Args:
            pr_data: Pull request data to analyze
            config: Provider-specific configuration
            
        Returns:
            ReviewResult: Analysis results and recommendations
            
        Raises:
            AIProviderError: When analysis fails
        """
        pass


class AIProviderError(Exception):
    """Custom exception for AI provider errors."""
    
    def __init__(self, message: str, provider: str = "unknown"):
        self.provider = provider
        super().__init__(f"[{provider}] {message}")
