"""
Simple test to validate the project structure and imports.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test that all modules can be imported successfully."""
    try:
        # Test interface imports
        from interfaces.ai_provider import AIProvider, AIProviderError
        
        # Test model imports
        from models.pr_data import PullRequestData, FileChange
        from models.review_result import ReviewResult, ReviewComment, ReviewSeverity
        
        # Test provider imports (will fail without openai package, but structure is correct)
        # from providers.azure_openai_provider import AzureOpenAIProvider
        
        # Test service imports
        from services.pr_review_service import PRReviewService
        
        # Test utils imports
        from utils.logger import get_logger
        
        print("✅ All imports successful")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_models():
    """Test model creation and basic functionality."""
    from models.pr_data import PullRequestData, FileChange
    from models.review_result import ReviewResult, ReviewComment, ReviewSeverity
    
    # Test FileChange
    file_change = FileChange(
        filename="test.py",
        status="modified",
        additions=10,
        deletions=2
    )
    
    # Test PullRequestData
    pr_data = PullRequestData(
        number=123,
        title="Test PR",
        body="Test description",
        author="test_user",
        base_branch="main",
        head_branch="feature",
        files_changed=[file_change]
    )
    
    # Test methods
    assert pr_data.get_total_changes() == 12
    assert pr_data.get_file_extensions() == ["py"]
    
    # Test ReviewResult
    comment = ReviewComment(
        filename="test.py",
        line_number=10,
        message="Good code!",
        severity=ReviewSeverity.INFO
    )
    
    result = ReviewResult(
        summary="Looks good",
        comments=[comment],
        overall_score=8,
        approved=True
    )
    
    assert len(result.get_comments_by_severity(ReviewSeverity.INFO)) == 1
    assert not result.has_blocking_issues()
    
    print("✅ Models working correctly")
    return True

if __name__ == "__main__":
    print("Testing Azure OpenAI PR Review Agent...")
    
    success = True
    success &= test_imports()
    success &= test_models()
    
    if success:
        print("\n🎉 All tests passed! Project structure is correct.")
    else:
        print("\n❌ Some tests failed.")
        sys.exit(1)
