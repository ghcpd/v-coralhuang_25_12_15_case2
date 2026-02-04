import unittest
from input_tools import ToolA as OrigToolA, ToolB as OrigToolB, ToolC as OrigToolC, HttpClient
from refactored_tools import ToolA as RefToolA, ToolB as RefToolB, ToolC as RefToolC


class BaseToolTestMixin:
    def setUp(self):
        self.client = HttpClient()
        self.base_url = "http://example.local"

    def _run_tool(self, tool_cls, user_id, query, limit=10):
        tool = tool_cls(self.client, self.base_url)
        return tool.run(user_id, query, limit=limit)


class TestOriginalTools(BaseToolTestMixin, unittest.TestCase):
    def test_toolA_valid(self):
        resp = self._run_tool(OrigToolA, "u1", "  hello  ")
        self.assertTrue(resp["ok"])
        # original ToolA uses camelCase "userId" and strips query
        expected = {"userId": "u1", "query": "hello", "limit": 10, "tool": "A"}
        self.assertEqual(resp["data"]["echo"], expected)

    def test_toolB_valid(self):
        resp = self._run_tool(OrigToolB, "u1", "  hello  ")
        self.assertTrue(resp["ok"])
        # original ToolB uses snake_case "user_id" and does not strip query
        expected = {"user_id": "u1", "query": "  hello  ", "limit": 10, "tool": "B"}
        self.assertEqual(resp["data"]["echo"], expected)

    def test_toolC_valid(self):
        resp = self._run_tool(OrigToolC, "u1", "  hello  ")
        self.assertTrue(resp["ok"])
        # original ToolC uses camelCase "userId" and key "q" with stripped
        expected = {"userId": "u1", "q": "hello", "limit": 10, "tool": "C"}
        self.assertEqual(resp["data"]["echo"], expected)

    def test_toolA_invalid(self):
        resp = self._run_tool(OrigToolA, "", "q")
        self.assertFalse(resp["ok"])
        self.assertIn("user_id is required", resp["error"])  # original message

        resp = self._run_tool(OrigToolA, "u1", "")
        self.assertFalse(resp["ok"])
        self.assertIn("query is required", resp["error"])

        resp = self._run_tool(OrigToolA, "u1", "q", limit=0)
        self.assertFalse(resp["ok"])
        self.assertIn("limit must be > 0", resp["error"])

    def test_toolB_invalid(self):
        resp = self._run_tool(OrigToolB, "", "q")
        self.assertFalse(resp["ok"])
        self.assertIn("missing user", resp["error"])

        resp = self._run_tool(OrigToolB, "u1", None)
        self.assertFalse(resp["ok"])
        self.assertIn("missing query", resp["error"])

        resp = self._run_tool(OrigToolB, "u1", "q", limit=-1)
        self.assertFalse(resp["ok"])
        self.assertIn("limit must be non-negative", resp["error"])

    def test_toolC_invalid(self):
        resp = self._run_tool(OrigToolC, "", "q")
        self.assertFalse(resp["ok"])
        self.assertIn("user_id required", resp["error"])

        resp = self._run_tool(OrigToolC, "u1", "")
        self.assertFalse(resp["ok"])
        self.assertIn("query must be non-empty string", resp["error"])

        resp = self._run_tool(OrigToolC, "u1", "q", limit=0)
        self.assertFalse(resp["ok"])
        self.assertIn("limit cannot be zero", resp["error"])


class TestRefactoredTools(BaseToolTestMixin, unittest.TestCase):
    def test_tool_valid_payloads_and_consistency(self):
        for cls, tool_name in [(RefToolA, "A"), (RefToolB, "B"), (RefToolC, "C")]:
            resp = self._run_tool(cls, "u1", "  hello  ")
            self.assertTrue(resp["ok"], f"{cls} should succeed")
            expected = {"user_id": "u1", "query": "hello", "limit": 10, "tool": tool_name}
            self.assertEqual(resp["data"]["echo"], expected)

    def test_tool_invalid_common_validation(self):
        resp = self._run_tool(RefToolA, "", "hello")
        self.assertFalse(resp["ok"])
        self.assertIn("user_id is required", resp["error"])

        resp = self._run_tool(RefToolB, "u1", None)
        self.assertFalse(resp["ok"])
        self.assertIn("query is required", resp["error"])

        resp = self._run_tool(RefToolC, "u1", "q", limit=0)
        self.assertFalse(resp["ok"])
        self.assertIn("limit must be > 0", resp["error"])
