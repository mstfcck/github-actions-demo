"""
Pull Request Data Model - Single Responsibility Principle.
Immutable data structure for PR information.
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class FileChange:
    """
    Represents a single file change.
    
    SOLID: Single Responsibility - only holds file change data
    """
    filename: str
    status: str  # 'added', 'modified', 'removed'
    additions: int
    deletions: int
    patch: Optional[str] = None


@dataclass(frozen=True)
class PullRequestData:
    """
    Pull request data structure.
    
    SOLID: Single Responsibility - aggregates PR information
    Immutable: Prevents accidental modifications (frozen=True)
    """
    number: int
    title: str
    body: str
    author: str
    base_branch: str
    head_branch: str
    files_changed: List[FileChange]
    
    def get_total_changes(self) -> int:
        """Calculate total lines changed."""
        return sum(fc.additions + fc.deletions for fc in self.files_changed)
    
    def get_file_extensions(self) -> List[str]:
        """Get unique file extensions from changed files."""
        extensions = set()
        for file_change in self.files_changed:
            if '.' in file_change.filename:
                ext = file_change.filename.split('.')[-1].lower()
                extensions.add(ext)
        return sorted(extensions)
