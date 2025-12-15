import json
import time
from typing import Any, Dict, Optional


class HttpClient:
    """Simple HTTP client simulator.

    Returns a simulated successful response that echoes the payload. This keeps
    the transport deterministic for tests and demonstrations.
    """

    def post(self, url: str, payload: Dict[str, Any], timeout_s: float = 10.0) -> Dict[str, Any]:
        # Simulated network latency
        time.sleep(0.001)
        return {"status_code": 200, "json": {"ok": True, "echo": payload}, "text": "OK"}


def _log(prefix: str, obj: Dict[str, Any]) -> None:
    # Preserve the basic logging behaviour used by the original tools.
    print(prefix + json.dumps(obj, sort_keys=True))


def _validate_inputs(user_id: Optional[str], query: Optional[str], limit: int) -> Optional[str]:
    """Shared validation rules for all tools.

    Rules (applied consistently across tools):
    - user_id must be a non-empty string
    - query must be a non-empty string after stripping
    - limit must be an integer > 0
    """
    if not isinstance(user_id, str) or user_id.strip() == "":
        return "user_id is required"

    if not isinstance(query, str) or query.strip() == "":
        return "query is required"

    if not isinstance(limit, int) or limit <= 0:
        return "limit must be > 0"

    return None


def _build_payload(user_id: str, query: str, limit: int, tool: str) -> Dict[str, Any]:
    """Construct a consistent payload format for all tools.

    Use camelCase keys and a stripped query to remove accidental whitespace.
    """
    return {
        "userId": user_id,
        "query": query.strip(),
        "limit": limit,
        "tool": tool,
    }


class BaseTool:
    """Shared behaviour for ToolA/ToolB/ToolC.

    Responsibilities separated:
    - input validation (shared)
    - payload construction (shared)
    - transport and response handling (shared)
    """

    TOOL_NAME = "base"

    def __init__(self, client: HttpClient, base_url: str) -> None:
        self.client = client
        self.base_url = base_url

    def _log_request(self, payload: Dict[str, Any]) -> None:
        _log(f"[{self.__class__.__name__}] request=", {"url": self.base_url + "/search", "payload": payload})

    def run(self, user_id: str, query: str, limit: int = 10, timeout_s: float = 10.0) -> Dict[str, Any]:
        # Validate using the unified rules
        err = _validate_inputs(user_id, query, limit)
        if err:
            return {"ok": False, "error": err}

        payload = _build_payload(user_id, query, limit, self.TOOL_NAME)

        # Log the request similarly to the original implementation
        self._log_request(payload)

        resp = self.client.post(self.base_url + "/search", payload, timeout_s=timeout_s)

        if resp.get("status_code") != 200:
            # Return structured error with raw response for debugging
            return {"ok": False, "error": f"bad status: {resp.get('status_code')}", "raw": resp}

        return {"ok": True, "data": resp.get("json"), "status_code": resp.get("status_code")}


class ToolA(BaseTool):
    TOOL_NAME = "A"


class ToolB(BaseTool):
    TOOL_NAME = "B"


class ToolC(BaseTool):
    TOOL_NAME = "C"
