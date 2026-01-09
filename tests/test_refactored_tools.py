import unittest

from refactored_tools import HttpClient, ToolA, ToolB, ToolC


class TestRefactoredTools(unittest.TestCase):
    def setUp(self):
        self.client = HttpClient()
        self.base_url = "http://example.local"

    def test_valid_input_tool_a(self):
        t = ToolA(self.client, self.base_url)
        res = t.run("u1", "  hello  ", limit=10)
        self.assertTrue(res.get("ok"))
        echo = res.get("data", {}).get("echo")
        self.assertIsInstance(echo, dict)
        self.assertEqual(echo.get("userId"), "u1")
        self.assertEqual(echo.get("query"), "hello")
        self.assertEqual(echo.get("limit"), 10)
        self.assertEqual(echo.get("tool"), "A")

    def test_valid_input_tool_b(self):
        t = ToolB(self.client, self.base_url)
        res = t.run("user42", "q", limit=5)
        self.assertTrue(res.get("ok"))
        echo = res.get("data", {}).get("echo")
        self.assertEqual(echo.get("userId"), "user42")
        self.assertEqual(echo.get("query"), "q")
        self.assertEqual(echo.get("limit"), 5)
        self.assertEqual(echo.get("tool"), "B")

    def test_valid_input_tool_c(self):
        t = ToolC(self.client, self.base_url)
        res = t.run("uX", " spaced ", limit=1)
        self.assertTrue(res.get("ok"))
        echo = res.get("data", {}).get("echo")
        self.assertEqual(echo.get("userId"), "uX")
        self.assertEqual(echo.get("query"), "spaced")
        self.assertEqual(echo.get("limit"), 1)
        self.assertEqual(echo.get("tool"), "C")

    def test_invalid_user_id(self):
        for cls in (ToolA, ToolB, ToolC):
            t = cls(self.client, self.base_url)
            res = t.run("", "ok", limit=1)
            self.assertFalse(res.get("ok"))
            self.assertIn("error", res)

    def test_invalid_query(self):
        for cls in (ToolA, ToolB, ToolC):
            t = cls(self.client, self.base_url)
            res = t.run("u1", "   ", limit=1)
            self.assertFalse(res.get("ok"))
            self.assertIn("error", res)

    def test_invalid_limit(self):
        for cls in (ToolA, ToolB, ToolC):
            t = cls(self.client, self.base_url)
            res = t.run("u1", "q", limit=0)
            self.assertFalse(res.get("ok"))
            self.assertIn("error", res)

    def test_payload_consistency_across_tools(self):
        tools = [ToolA(self.client, self.base_url), ToolB(self.client, self.base_url), ToolC(self.client, self.base_url)]
        echoes = []
        for t in tools:
            res = t.run("u1", "  hello  ", limit=3)
            self.assertTrue(res.get("ok"))
            echoes.append(res.get("data", {}).get("echo"))

        # All echoes should have identical key sets and the query should be stripped
        keyset = set(echoes[0].keys())
        for e in echoes[1:]:
            self.assertEqual(set(e.keys()), keyset)
            self.assertEqual(e.get("query"), "hello")


if __name__ == "__main__":
    unittest.main()
