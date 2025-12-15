import os
import sys
import unittest
import io
import json
from contextlib import redirect_stdout

# Ensure tests import the package when running from the tests/ dir
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from refactored_tools import HttpClient, ToolA, ToolB, ToolC


class DummyClient(HttpClient):
    def __init__(self):
        super().__init__()
        self.last_request = None

    def post(self, url, payload, timeout_s=10.0):
        self.last_request = {"url": url, "payload": payload, "timeout_s": timeout_s}
        return super().post(url, payload, timeout_s=timeout_s)


class ToolTests(unittest.TestCase):
    def setUp(self):
        self.client = DummyClient()
        self.base_url = "http://example.local"
        self.tools = [ToolA(self.client, self.base_url), ToolB(self.client, self.base_url), ToolC(self.client, self.base_url)]

    def test_valid_requests(self):
        for t in self.tools:
            f = io.StringIO()
            with redirect_stdout(f):
                res = t.run("u1", "  hello  ", limit=10)
            out = f.getvalue()

            self.assertTrue(res["ok"])
            self.assertEqual(res["status_code"], 200)
            data = res["data"]
            self.assertIn("echo", data)
            echo = data["echo"]

            # Payload format consistency
            self.assertEqual(echo["userId"], "u1")
            self.assertEqual(echo["query"], "hello")
            self.assertEqual(echo["limit"], 10)
            self.assertEqual(echo["tool"], t.TOOL_NAME)

            # Basic logging behavior
            self.assertIn(f"[{t.__class__.__name__}] request=", out)

    def test_invalid_user_id(self):
        for t in self.tools:
            res = t.run("", "hello", limit=1)
            self.assertFalse(res["ok"]) 
            self.assertIn("user_id", res["error"]) 

    def test_invalid_query(self):
        for t in self.tools:
            res = t.run("u1", "   ", limit=1)
            self.assertFalse(res["ok"]) 
            self.assertIn("query", res["error"]) 

    def test_invalid_limit(self):
        for t in self.tools:
            res = t.run("u1", "hi", limit=0)
            self.assertFalse(res["ok"]) 
            self.assertIn("limit", res["error"]) 


if __name__ == "__main__":
    unittest.main()
