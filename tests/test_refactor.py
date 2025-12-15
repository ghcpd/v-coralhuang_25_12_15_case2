import unittest
from refactored.tools import ToolA, ToolB, ToolC


class FakeClient:
    def __init__(self):
        self.calls = []

    def post(self, url, payload, timeout_s=10.0):
        self.calls.append({"url": url, "payload": payload, "timeout_s": timeout_s})
        return {"status_code": 200, "json": {"ok": True, "echo": payload}, "text": "OK"}


class FakeBadClient(FakeClient):
    def post(self, url, payload, timeout_s=10.0):
        self.calls.append({"url": url, "payload": payload, "timeout_s": timeout_s})
        return {"status_code": 500, "json": {"ok": False}, "text": "ERR"}


class ToolTests(unittest.TestCase):
    def test_valid_inputs_and_payload_format(self):
        client = FakeClient()
        base = "http://example.com"

        for ToolCls, name in [(ToolA, "A"), (ToolB, "B"), (ToolC, "C")]:
            t = ToolCls(client, base)
            res = t.run("user123", "  hello world  ", limit=5, timeout_s=2.0)
            self.assertTrue(res["ok"])
            self.assertEqual(res["status_code"], 200)
            # last call payload
            last = client.calls[-1]
            self.assertEqual(last["url"], base + "/search")
            payload = last["payload"]
            self.assertEqual(payload["userId"], "user123")
            self.assertEqual(payload["query"], "hello world")
            self.assertEqual(payload["limit"], 5)
            self.assertEqual(payload["tool"], name)

    def test_invalid_user_id(self):
        client = FakeClient()
        t = ToolA(client, "http://x")
        res = t.run("", "q", limit=1)
        self.assertFalse(res["ok"])  

    def test_invalid_query(self):
        client = FakeClient()
        t = ToolB(client, "http://x")
        res = t.run("u", "", limit=1)
        self.assertFalse(res["ok"])  

    def test_invalid_limit(self):
        client = FakeClient()
        t = ToolC(client, "http://x")
        res = t.run("u", "q", limit=0)
        self.assertFalse(res["ok"])  

    def test_transport_error_is_returned(self):
        client = FakeBadClient()
        t = ToolA(client, "http://x")
        res = t.run("u", "q", limit=1)
        self.assertFalse(res["ok"]) 
        self.assertIn("raw", res)


if __name__ == "__main__":
    unittest.main()
