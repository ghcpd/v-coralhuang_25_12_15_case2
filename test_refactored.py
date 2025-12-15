"""
Comprehensive test suite for refactored tools.

Tests cover:
- Input validation for each tool
- Payload structure consistency
- HTTP response handling
- Backward compatibility with original behavior
"""

import sys
import unittest
from typing import Dict, Any
from refactored_tools import (
    HttpClient,
    InputValidator,
    PayloadBuilder,
    ToolA,
    ToolB,
    ToolC,
)


class MockHttpClient(HttpClient):
    """Mock HTTP client for testing that records requests."""
    
    def __init__(self):
        self.last_request = None
        self.last_url = None
    
    def post(self, url: str, payload: Dict[str, Any], timeout_s: float = 10.0) -> Dict[str, Any]:
        self.last_url = url
        self.last_request = payload
        return {"status_code": 200, "json": {"ok": True, "echo": payload}, "text": "OK"}


class TestInputValidator(unittest.TestCase):
    """Tests for InputValidator class."""
    
    def test_validate_user_id_empty_string(self):
        """Empty user_id should be invalid."""
        error = InputValidator.validate_user_id("")
        self.assertIsNotNone(error)
        self.assertIn("required", error)
    
    def test_validate_user_id_none(self):
        """None user_id should be invalid."""
        error = InputValidator.validate_user_id(None)
        self.assertIsNotNone(error)
    
    def test_validate_user_id_valid(self):
        """Valid user_id should pass."""
        error = InputValidator.validate_user_id("user123")
        self.assertIsNone(error)
    
    def test_validate_query_empty_string(self):
        """Empty query should be invalid."""
        error = InputValidator.validate_query("")
        self.assertIsNotNone(error)
    
    def test_validate_query_none(self):
        """None query should be invalid."""
        error = InputValidator.validate_query(None)
        self.assertIsNotNone(error)
    
    def test_validate_query_valid(self):
        """Valid query should pass."""
        error = InputValidator.validate_query("hello")
        self.assertIsNone(error)
    
    def test_validate_query_non_string(self):
        """Non-string query should be invalid."""
        error = InputValidator.validate_query(123)
        self.assertIsNotNone(error)
    
    def test_validate_limit_zero(self):
        """Limit of 0 should be invalid with default min_value=1."""
        error = InputValidator.validate_limit(0)
        self.assertIsNotNone(error)
    
    def test_validate_limit_negative(self):
        """Negative limit should be invalid."""
        error = InputValidator.validate_limit(-1)
        self.assertIsNotNone(error)
    
    def test_validate_limit_valid(self):
        """Valid limit should pass."""
        error = InputValidator.validate_limit(10)
        self.assertIsNone(error)
    
    def test_validate_limit_custom_min(self):
        """Custom min_value should be respected."""
        error = InputValidator.validate_limit(0, min_value=0)
        self.assertIsNone(error)


class TestPayloadBuilder(unittest.TestCase):
    """Tests for PayloadBuilder class."""
    
    def test_basic_payload(self):
        """Basic payload should have required fields."""
        payload = PayloadBuilder.build(
            user_id="user1",
            query="hello",
            limit=10,
            tool_name="A",
        )
        
        self.assertEqual(payload["userId"], "user1")
        self.assertEqual(payload["query"], "hello")
        self.assertEqual(payload["limit"], 10)
        self.assertEqual(payload["tool"], "A")
    
    def test_query_stripping(self):
        """Query with strip_query=True should be stripped."""
        payload = PayloadBuilder.build(
            user_id="user1",
            query="  hello  ",
            limit=10,
            tool_name="A",
            strip_query=True,
        )
        self.assertEqual(payload["query"], "hello")
    
    def test_query_no_stripping(self):
        """Query with strip_query=False should not be stripped."""
        payload = PayloadBuilder.build(
            user_id="user1",
            query="  hello  ",
            limit=10,
            tool_name="A",
            strip_query=False,
        )
        self.assertEqual(payload["query"], "  hello  ")
    
    def test_custom_query_key(self):
        """Custom query_key should be used in payload."""
        payload = PayloadBuilder.build(
            user_id="user1",
            query="hello",
            limit=10,
            tool_name="C",
            query_key="q",
        )
        self.assertIn("q", payload)
        self.assertNotIn("query", payload)
        self.assertEqual(payload["q"], "hello")
    
    def test_custom_fields(self):
        """Custom fields should be added to payload."""
        custom = {"extra": "field", "priority": 5}
        payload = PayloadBuilder.build(
            user_id="user1",
            query="hello",
            limit=10,
            tool_name="A",
            custom_fields=custom,
        )
        self.assertEqual(payload["extra"], "field")
        self.assertEqual(payload["priority"], 5)


class TestToolA(unittest.TestCase):
    """Tests for ToolA refactored implementation."""
    
    def setUp(self):
        self.client = MockHttpClient()
        self.tool = ToolA(self.client, "http://api.test")
    
    def test_valid_input(self):
        """Valid inputs should return success."""
        result = self.tool.run("user1", "query", limit=10)
        
        self.assertTrue(result["ok"])
        self.assertIn("data", result)
        self.assertEqual(result["status_code"], 200)
    
    def test_invalid_user_id(self):
        """Empty user_id should fail."""
        result = self.tool.run("", "query", limit=10)
        
        self.assertFalse(result["ok"])
        self.assertIn("error", result)
        self.assertIn("required", result["error"])
    
    def test_invalid_query(self):
        """Empty query should fail."""
        result = self.tool.run("user1", "", limit=10)
        
        self.assertFalse(result["ok"])
        self.assertIn("error", result)
    
    def test_invalid_limit_zero(self):
        """Limit of 0 should fail."""
        result = self.tool.run("user1", "query", limit=0)
        
        self.assertFalse(result["ok"])
        self.assertIn("error", result)
    
    def test_payload_has_query_key(self):
        """Payload should use 'query' key, not 'q'."""
        self.tool.run("user1", "test", limit=10)
        
        self.assertIn("query", self.client.last_request)
        self.assertNotIn("q", self.client.last_request)
    
    def test_payload_strips_query(self):
        """Query should be stripped of whitespace."""
        self.tool.run("user1", "  test  ", limit=10)
        
        self.assertEqual(self.client.last_request["query"], "test")
    
    def test_payload_uses_camelcase_userid(self):
        """Payload should use 'userId' (camelCase) key."""
        self.tool.run("user123", "query", limit=10)
        
        self.assertEqual(self.client.last_request["userId"], "user123")
        self.assertNotIn("user_id", self.client.last_request)


class TestToolB(unittest.TestCase):
    """Tests for ToolB refactored implementation."""
    
    def setUp(self):
        self.client = MockHttpClient()
        self.tool = ToolB(self.client, "http://api.test")
    
    def test_valid_input(self):
        """Valid inputs should return success."""
        result = self.tool.run("user1", "query", limit=10)
        
        self.assertTrue(result["ok"])
        self.assertIn("data", result)
    
    def test_invalid_user_id(self):
        """Empty user_id should fail."""
        result = self.tool.run("", "query", limit=10)
        
        self.assertFalse(result["ok"])
    
    def test_limit_consistency_with_a(self):
        """Limit validation should be consistent with ToolA."""
        # Both should reject limit=0
        result_a = ToolA(self.client, "http://api.test").run("user1", "q", limit=0)
        result_b = ToolB(self.client, "http://api.test").run("user1", "q", limit=0)
        
        self.assertFalse(result_a["ok"])
        self.assertFalse(result_b["ok"])
    
    def test_payload_does_not_strip_query(self):
        """Query should NOT be stripped for ToolB."""
        self.tool.run("user1", "  test  ", limit=10)
        
        self.assertEqual(self.client.last_request["query"], "  test  ")


class TestToolC(unittest.TestCase):
    """Tests for ToolC refactored implementation."""
    
    def setUp(self):
        self.client = MockHttpClient()
        self.tool = ToolC(self.client, "http://api.test")
    
    def test_valid_input(self):
        """Valid inputs should return success."""
        result = self.tool.run("user1", "query", limit=10)
        
        self.assertTrue(result["ok"])
        self.assertIn("data", result)
    
    def test_limit_zero_now_allowed(self):
        """Limit of 0 should now fail (consistent with A and B)."""
        result = self.tool.run("user1", "query", limit=0)
        
        self.assertFalse(result["ok"])
    
    def test_payload_uses_q_key(self):
        """Payload should use 'q' key for query."""
        self.tool.run("user1", "test", limit=10)
        
        self.assertIn("q", self.client.last_request)
        self.assertNotIn("query", self.client.last_request)
    
    def test_payload_strips_query(self):
        """Query should be stripped of whitespace."""
        self.tool.run("user1", "  test  ", limit=10)
        
        self.assertEqual(self.client.last_request["q"], "test")
    
    def test_limit_consistency_with_a(self):
        """Limit validation should be consistent with ToolA."""
        # Both should reject limit=0
        result_a = ToolA(self.client, "http://api.test").run("user1", "q", limit=0)
        result_c = ToolC(self.client, "http://api.test").run("user1", "q", limit=0)
        
        self.assertFalse(result_a["ok"])
        self.assertFalse(result_c["ok"])


class TestBackwardCompatibility(unittest.TestCase):
    """Tests to ensure backward compatibility with original implementation."""
    
    def setUp(self):
        self.client = MockHttpClient()
        self.base_url = "http://api.test"
    
    def test_all_tools_have_run_method(self):
        """All tools should have a run method."""
        for tool_class in [ToolA, ToolB, ToolC]:
            tool = tool_class(self.client, self.base_url)
            self.assertTrue(callable(getattr(tool, "run", None)))
    
    def test_run_method_signature(self):
        """run method should accept user_id, query, limit, timeout_s."""
        tool = ToolA(self.client, self.base_url)
        result = tool.run("user1", "query", limit=10, timeout_s=5.0)
        self.assertIsInstance(result, dict)
    
    def test_response_format_success(self):
        """Successful response should have ok=True and data."""
        tool = ToolA(self.client, self.base_url)
        result = tool.run("user1", "query", limit=10)
        
        self.assertIn("ok", result)
        self.assertIn("data", result)
        self.assertIn("status_code", result)
        self.assertTrue(result["ok"])
    
    def test_response_format_error(self):
        """Error response should have ok=False and error."""
        tool = ToolA(self.client, self.base_url)
        result = tool.run("", "query", limit=10)
        
        self.assertIn("ok", result)
        self.assertIn("error", result)
        self.assertFalse(result["ok"])
    
    def test_default_limit(self):
        """Default limit should be 10."""
        tool = ToolA(self.client, self.base_url)
        tool.run("user1", "query")
        
        self.assertEqual(self.client.last_request["limit"], 10)


def run_tests():
    """Run all tests and return exit code."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestInputValidator))
    suite.addTests(loader.loadTestsFromTestCase(TestPayloadBuilder))
    suite.addTests(loader.loadTestsFromTestCase(TestToolA))
    suite.addTests(loader.loadTestsFromTestCase(TestToolB))
    suite.addTests(loader.loadTestsFromTestCase(TestToolC))
    suite.addTests(loader.loadTestsFromTestCase(TestBackwardCompatibility))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return appropriate exit code
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(run_tests())
