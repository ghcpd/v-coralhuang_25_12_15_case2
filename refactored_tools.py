import json
import time
from typing import Dict, Any, Optional
from input_tools import HttpClient, _log


class BaseTool:
    def __init__(self, client: HttpClient, base_url: str):
        self.client = client
        self.base_url = base_url

    def _validate(self, user_id: str, query: str, limit: int) -> Optional[str]:
        if not user_id or not user_id.strip():
            return "user_id is required"
        if query is None or not query.strip():
            return "query is required"
        if limit <= 0:
            return "limit must be > 0"
        return None

    def _build_payload(self, user_id: str, query: str, limit: int) -> Dict[str, Any]:
        raise NotImplementedError

    def _log_request(self, url: str, payload: Dict[str, Any]):
        _log(f"[{self.__class__.__name__}] request=", {"url": url, "payload": payload})

    def _handle_error(self, resp: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError

    def run(self, user_id: str, query: str, limit: int = 10, timeout_s: float = 10.0) -> Dict[str, Any]:
        error = self._validate(user_id, query, limit)
        if error:
            return {"ok": False, "error": error}
        payload = self._build_payload(user_id, query, limit)
        self._log_request(self.base_url + "/search", payload)
        resp = self.client.post(self.base_url + "/search", payload, timeout_s=timeout_s)
        if resp.get("status_code") != 200:
            return self._handle_error(resp)
        return {"ok": True, "data": resp.get("json"), "status_code": resp.get("status_code")}


class ToolA(BaseTool):
    def _build_payload(self, user_id: str, query: str, limit: int) -> Dict[str, Any]:
        return {
            "userId": user_id,
            "query": query.strip(),
            "limit": limit,
            "tool": "A",
        }

    def _handle_error(self, resp: Dict[str, Any]) -> Dict[str, Any]:
        return {"ok": False, "error": f"bad status: {resp.get('status_code')}", "raw": resp}


class ToolB(BaseTool):
    def _build_payload(self, user_id: str, query: str, limit: int) -> Dict[str, Any]:
        return {
            "user_id": user_id,
            "query": query,
            "limit": limit,
            "tool": "B",
        }

    def _handle_error(self, resp: Dict[str, Any]) -> Dict[str, Any]:
        return {"ok": False, "error": "request failed", "raw": resp}


class ToolC(BaseTool):
    def _build_payload(self, user_id: str, query: str, limit: int) -> Dict[str, Any]:
        return {
            "userId": user_id,
            "q": query.strip(),
            "limit": limit,
            "tool": "C",
        }

    def _handle_error(self, resp: Dict[str, Any]) -> Dict[str, Any]:
        return {"ok": False, "error": f"HTTP {resp.get('status_code')}", "raw": resp}