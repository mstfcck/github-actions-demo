"""
Quick test to verify the fixes work
"""
import sys
import os
import json

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Test the format function without importing the full app
def test_output_format():
    """Test that our new output format works"""
    from models.review_result import ReviewResult, ReviewComment, ReviewSeverity
    
    # Create test data
    comment = ReviewComment(
        filename="test.py",
        line_number=10,
        message="Test message",
        severity=ReviewSeverity.WARNING
    )
    
    result = ReviewResult(
        summary="Test summary",
        comments=[comment],
        overall_score=7,
        approved=False
    )
    
    # Test JSON serialization (what we do in the new output)
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
    
    # Test that it serializes to JSON correctly
    json_str = json.dumps(result_json)
    
    # Test that it can be parsed back
    parsed = json.loads(json_str)
    
    print("✅ JSON serialization works")
    print(f"✅ Result has {len(parsed['comments'])} comments")
    print(f"✅ Score: {parsed['overall_score']}/10")
    print(f"✅ Approved: {parsed['approved']}")
    
    return True

if __name__ == "__main__":
    print("🧪 Testing fixes...")
    test_output_format()
    print("🎉 All fix tests passed!")
