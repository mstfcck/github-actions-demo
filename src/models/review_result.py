"""
Review Result Model - Single Responsibility Principle.
Immutable data structure for review results.
"""

from dataclasses import dataclass
from typing import List, Optional
from enum import Enum


class ReviewSeverity(Enum):
    """Review severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


@dataclass(frozen=True)
class ReviewComment:
    """
    Individual review comment.
    
    SOLID: Single Responsibility - holds one review comment
    """
    line_number: Optional[int]
    filename: Optional[str]
    message: str
    severity: ReviewSeverity = ReviewSeverity.INFO


@dataclass(frozen=True)
class ReviewResult:
    """
    Complete review result.
    
    SOLID: Single Responsibility - aggregates review information
    Immutable: Prevents accidental modifications
    """
    summary: str
    comments: List[ReviewComment]
    overall_score: int  # 1-10 scale
    approved: bool
    
    def get_comments_by_severity(self, severity: ReviewSeverity) -> List[ReviewComment]:
        """Filter comments by severity level."""
        return [comment for comment in self.comments if comment.severity == severity]
    
    def has_blocking_issues(self) -> bool:
        """Check if there are any error-level comments."""
        return any(comment.severity == ReviewSeverity.ERROR for comment in self.comments)
