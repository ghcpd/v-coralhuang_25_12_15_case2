import json
import time
from typing import Dict, Any, Optional


class HttpClient:
    def post(self, url: str, payload: Dict[str, Any], timeout_s: float = 10.0) -> Dict[str, Any]:
        # Fake transport (simulated response)
        time.sleep(0.01)
        return {"status_code": 200, "json": {"ok": True, "echo": payload}, "text": "OK"}


def _log(prefix: str, obj: Dict[str, Any]) -> None:
    print(prefix + json.dumps(obj, sort_keys=True))


class ToolA:
    def __init__(self, client: HttpClient, base_url: str):
        self.client = client
        self.base_url = base_url

    def run(self, user_id: str, query: str, limit: int = 10, timeout_s: float = 10.0) -> Dict[str, Any]:
        # Validation (duplicated)
        if not user_id:
            return {"ok": False, "error": "user_id is required"}
        if query is None or query == "":
            return {"ok": False, "error": "query is required"}
        if limit <= 0:
            return {"ok": False, "error": "limit must be > 0"}

        payload = {
            "userId": user_id,          # camelCase here
            "query": query.strip(),
            "limit": limit,
            "tool": "A",
        }

        _log("[ToolA] request=", {"url": self.base_url + "/search", "payload": payload})
        resp = self.client.post(self.base_url + "/search", payload, timeout_s=timeout_s)

        if resp.get("status_code") != 200:
            return {"ok": False, "error": f"bad status: {resp.get('status_code')}", "raw": resp}

        return {"ok": True, "data": resp.get("json"), "status_code": resp.get("status_code")}


class ToolB:
    def __init__(self, client: HttpClient, base_url: str):
        self.client = client
        self.base_url = base_url

    def run(self, user_id: str, query: str, limit: int = 10, timeout_s: float = 10.0) -> Dict[str, Any]:
        # Validation (duplicated but inconsistent)
        if user_id is None or user_id == "":
            return {"ok": False, "error": "missing user"}
        if query is None:
            return {"ok": False, "error": "missing query"}
        if limit < 0:  # bug: allows 0
            return {"ok": False, "error": "limit must be non-negative"}

        payload = {
            "user_id": user_id,         # snake_case here (inconsistent!)
            "query": query,             # not stripped
            "limit": limit,
            "tool": "B",
        }

        _log("[ToolB] request=", {"url": self.base_url + "/search", "payload": payload})
        resp = self.client.post(self.base_url + "/search", payload, timeout_s=timeout_s)

        if resp.get("status_code") != 200:
            return {"ok": False, "error": "request failed", "raw": resp}

        return {"ok": True, "data": resp.get("json"), "status_code": resp.get("status_code")}


class ToolC:
    def __init__(self, client: HttpClient, base_url: str):
        self.client = client
        self.base_url = base_url

    def run(self, user_id: str, query: str, limit: int = 10, timeout_s: float = 10.0) -> Dict[str, Any]:
        # Validation (duplicated but inconsistent)
        if not user_id:
            return {"ok": False, "error": "user_id required"}
        if not isinstance(query, str) or query == "":
            return {"ok": False, "error": "query must be non-empty string"}
        if limit == 0:  # bug: rejects 0 but ToolB allows 0
            return {"ok": False, "error": "limit cannot be zero"}

        payload = {
            "userId": user_id,
            "q": query.strip(),         # key differs again: q
            "limit": limit,
            "tool": "C",
        }

        _log("[ToolC] request=", {"url": self.base_url + "/search", "payload": payload})
        resp = self.client.post(self.base_url + "/search", payload, timeout_s=timeout_s)

        if resp.get("status_code") != 200:
            return {"ok": False, "error": f"HTTP {resp.get('status_code')}", "raw": resp}

        return {"ok": True, "data": resp.get("json"), "status_code": resp.get("status_code")}
