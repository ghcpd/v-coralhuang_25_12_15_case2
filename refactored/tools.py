import json
from typing import Dict, Any


def _log(prefix: str, obj: Dict[str, Any]) -> None:
    # Keep the same basic logging behaviour (prefix + JSON) for compatibility
    print(prefix + json.dumps(obj, sort_keys=True))


class ValidationError(Exception):
    pass


def validate_inputs(user_id: str, query: str, limit: int) -> None:
    if not isinstance(user_id, str) or user_id.strip() == "":
        raise ValidationError("user_id is required")
    if not isinstance(query, str) or query.strip() == "":
        raise ValidationError("query is required")
    if not isinstance(limit, int) or limit <= 0:
        raise ValidationError("limit must be > 0")


class BaseTool:
    def __init__(self, client, base_url: str, tool_name: str):
        self.client = client
        self.base_url = base_url
        self.tool_name = tool_name

    def _build_payload(self, user_id: str, query: str, limit: int) -> Dict[str, Any]:
        # Standardized payload: camelCase keys, stripped query
        return {
            "userId": user_id,
            "query": query.strip(),
            "limit": limit,
            "tool": self.tool_name,
        }

    def _transport(self, payload: Dict[str, Any], timeout_s: float) -> Dict[str, Any]:
        url = self.base_url + "/search"
        _log(f"[{self.tool_name}] request=", {"url": url, "payload": payload})
        resp = self.client.post(url, payload, timeout_s=timeout_s)
        return resp

    def run(self, user_id: str, query: str, limit: int = 10, timeout_s: float = 10.0) -> Dict[str, Any]:
        try:
            validate_inputs(user_id, query, limit)
        except ValidationError as exc:
            return {"ok": False, "error": str(exc)}

        payload = self._build_payload(user_id, query, limit)
        resp = self._transport(payload, timeout_s=timeout_s)

        if resp.get("status_code") != 200:
            return {"ok": False, "error": f"bad status: {resp.get('status_code')}", "raw": resp}

        return {"ok": True, "data": resp.get("json"), "status_code": resp.get("status_code")}


# Public tool classes preserve names and interfaces
class ToolA(BaseTool):
    def __init__(self, client, base_url: str):
        super().__init__(client, base_url, "A")


class ToolB(BaseTool):
    def __init__(self, client, base_url: str):
        super().__init__(client, base_url, "B")


class ToolC(BaseTool):
    def __init__(self, client, base_url: str):
        super().__init__(client, base_url, "C")
