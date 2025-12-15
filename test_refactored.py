import unittest
from refactored_tools import ToolA, ToolB, ToolC
from input_tools import HttpClient


class TestTools(unittest.TestCase):
    def setUp(self):
        self.client = HttpClient()
        self.base_url = "http://example.local"

    def test_tool_a_valid(self):
        tool = ToolA(self.client, self.base_url)
        result = tool.run("u1", "hello", 10)
        self.assertTrue(result["ok"])
        self.assertEqual(result["status_code"], 200)
        payload = result["data"]["echo"]
        self.assertEqual(payload["userId"], "u1")
        self.assertEqual(payload["query"], "hello")
        self.assertEqual(payload["limit"], 10)
        self.assertEqual(payload["tool"], "A")

    def test_tool_a_invalid_user(self):
        tool = ToolA(self.client, self.base_url)
        result = tool.run("", "hello", 10)
        self.assertFalse(result["ok"])
        self.assertEqual(result["error"], "user_id is required")

    def test_tool_a_invalid_query(self):
        tool = ToolA(self.client, self.base_url)
        result = tool.run("u1", "", 10)
        self.assertFalse(result["ok"])
        self.assertEqual(result["error"], "query is required")

    def test_tool_a_invalid_limit(self):
        tool = ToolA(self.client, self.base_url)
        result = tool.run("u1", "hello", 0)
        self.assertFalse(result["ok"])
        self.assertEqual(result["error"], "limit must be > 0")

    def test_tool_b_valid(self):
        tool = ToolB(self.client, self.base_url)
        result = tool.run("u1", "  hello  ", 10)
        self.assertTrue(result["ok"])
        self.assertEqual(result["status_code"], 200)
        payload = result["data"]["echo"]
        self.assertEqual(payload["user_id"], "u1")
        self.assertEqual(payload["query"], "  hello  ")
        self.assertEqual(payload["limit"], 10)
        self.assertEqual(payload["tool"], "B")

    def test_tool_b_invalid_user(self):
        tool = ToolB(self.client, self.base_url)
        result = tool.run("", "hello", 10)
        self.assertFalse(result["ok"])
        self.assertEqual(result["error"], "user_id is required")

    def test_tool_b_invalid_query(self):
        tool = ToolB(self.client, self.base_url)
        result = tool.run("u1", None, 10)
        self.assertFalse(result["ok"])
        self.assertEqual(result["error"], "query is required")

    def test_tool_b_invalid_limit(self):
        tool = ToolB(self.client, self.base_url)
        result = tool.run("u1", "hello", 0)
        self.assertFalse(result["ok"])
        self.assertEqual(result["error"], "limit must be > 0")

    def test_tool_c_valid(self):
        tool = ToolC(self.client, self.base_url)
        result = tool.run("u1", "  hello  ", 10)
        self.assertTrue(result["ok"])
        self.assertEqual(result["status_code"], 200)
        payload = result["data"]["echo"]
        self.assertEqual(payload["userId"], "u1")
        self.assertEqual(payload["q"], "hello")
        self.assertEqual(payload["limit"], 10)
        self.assertEqual(payload["tool"], "C")

    def test_tool_c_invalid_user(self):
        tool = ToolC(self.client, self.base_url)
        result = tool.run("", "hello", 10)
        self.assertFalse(result["ok"])
        self.assertEqual(result["error"], "user_id is required")

    def test_tool_c_invalid_query(self):
        tool = ToolC(self.client, self.base_url)
        result = tool.run("u1", "", 10)
        self.assertFalse(result["ok"])
        self.assertEqual(result["error"], "query is required")

    def test_tool_c_invalid_limit(self):
        tool = ToolC(self.client, self.base_url)
        result = tool.run("u1", "hello", 0)
        self.assertFalse(result["ok"])
        self.assertEqual(result["error"], "limit must be > 0")