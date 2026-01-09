from typing import Dict, Any, Optional
from .client import HttpClient, _log


class ValidationError(Exception):
    pass


class BaseTool:
    """Shared base class that encapsulates validation, payload building and transport."""

    TOOL_NAME = ""

    def __init__(self, client: HttpClient, base_url: str):
        self.client = client
        self.base_url = base_url.rstrip("/")

    def validate(self, user_id: str, query: str, limit: int) -> None:
        # Unified validation rules for all tools
        if not isinstance(user_id, str) or user_id.strip() == "":
            raise ValidationError("user_id is required")
        if not isinstance(query, str) or query.strip() == "":
            raise ValidationError("query is required")
        if not isinstance(limit, int) or limit <= 0:
            raise ValidationError("limit must be > 0")

    def build_payload(self, user_id: str, query: str, limit: int) -> Dict[str, Any]:
        # Consistent payload format across tools
        return {
            "userId": user_id.strip(),
            "query": query.strip(),
            "limit": limit,
            "tool": self.TOOL_NAME,
        }

    def _send(self, payload: Dict[str, Any], timeout_s: float = 10.0) -> Dict[str, Any]:
        url = self.base_url + "/search"
        _log(f"[{self.__class__.__name__}] request=", {"url": url, "payload": payload})
        resp = self.client.post(url, payload, timeout_s=timeout_s)

        if resp.get("status_code") != 200:
            return {"ok": False, "error": f"bad status: {resp.get('status_code')}", "raw": resp}

        return {"ok": True, "data": resp.get("json"), "status_code": resp.get("status_code")}

    def run(self, user_id: str, query: str, limit: int = 10, timeout_s: float = 10.0) -> Dict[str, Any]:
        # Public method kept for compatibility; delegating to helpers
        try:
            self.validate(user_id, query, limit)
        except ValidationError as e:
            return {"ok": False, "error": str(e)}

        payload = self.build_payload(user_id, query, limit)
        return self._send(payload, timeout_s=timeout_s)
