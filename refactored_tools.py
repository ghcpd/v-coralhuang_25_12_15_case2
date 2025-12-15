import json
from typing import Dict, Any, Optional


class HttpClient:
    """Same simple fake HTTP client used by original tools.

    This class is included here so the refactored tools can be run
    independently without modifying existing code.
    """

    def post(self, url: str, payload: Dict[str, Any], timeout_s: float = 10.0) -> Dict[str, Any]:
        # Fake transport (simulated response)
        return {"status_code": 200, "json": {"ok": True, "echo": payload}, "text": "OK"}


def _log(prefix: str, obj: Dict[str, Any]) -> None:
    print(prefix + json.dumps(obj, sort_keys=True))


class BaseTool:
    """Shared behavior for all tools.

    * common input validation
    * common payload construction shape
    * request logging
    * common response handler
    """

    def __init__(self, client: HttpClient, base_url: str):
        self.client = client
        self.base_url = base_url

    def _validate(self, user_id: Optional[str], query: Optional[str], limit: int) -> Optional[str]:
        if not user_id or not isinstance(user_id, str):
            return "user_id is required"
        if not query or not isinstance(query, str):
            return "query is required"
        if not isinstance(limit, int) or limit <= 0:
            return "limit must be > 0"
        return None

    def _build_payload(self, user_id: str, query: str, limit: int, tool_name: str) -> Dict[str, Any]:
        # Always use snake_case keys and strip whitespace from query
        return {
            "user_id": user_id,
            "query": query.strip(),
            "limit": limit,
            "tool": tool_name,
        }

    def _send(self, url: str, payload: Dict[str, Any], timeout_s: float, log_prefix: str) -> Dict[str, Any]:
        _log(log_prefix, {"url": url, "payload": payload})
        resp = self.client.post(url, payload, timeout_s=timeout_s)
        if resp.get("status_code") != 200:
            return {"ok": False, "error": f"bad status: {resp.get('status_code')}", "raw": resp}
        return {"ok": True, "data": resp.get("json"), "status_code": resp.get("status_code")}


class ToolA(BaseTool):
    def run(self, user_id: str, query: str, limit: int = 10, timeout_s: float = 10.0) -> Dict[str, Any]:
        err = self._validate(user_id, query, limit)
        if err:
            return {"ok": False, "error": err}
        payload = self._build_payload(user_id, query, limit, "A")
        return self._send(self.base_url + "/search", payload, timeout_s, "[ToolA] request=")


class ToolB(BaseTool):
    def run(self, user_id: str, query: str, limit: int = 10, timeout_s: float = 10.0) -> Dict[str, Any]:
        err = self._validate(user_id, query, limit)
        if err:
            return {"ok": False, "error": err}
        payload = self._build_payload(user_id, query, limit, "B")
        return self._send(self.base_url + "/search", payload, timeout_s, "[ToolB] request=")


class ToolC(BaseTool):
    def run(self, user_id: str, query: str, limit: int = 10, timeout_s: float = 10.0) -> Dict[str, Any]:
        err = self._validate(user_id, query, limit)
        if err:
            return {"ok": False, "error": err}
        payload = self._build_payload(user_id, query, limit, "C")
        return self._send(self.base_url + "/search", payload, timeout_s, "[ToolC] request=")
