import json
import time
from typing import Dict, Any


class HttpClient:
    """A small HTTP client shim used by the tools.

    This mirrors the behavior of the original input_tools.HttpClient: a fake transport
    that sleeps briefly and returns a dict with status_code, json and text. Keeping this
    small dependency here makes the refactor self-contained and compatible with tests.
    """

    def post(self, url: str, payload: Dict[str, Any], timeout_s: float = 10.0) -> Dict[str, Any]:
        # Simulate network latency
        time.sleep(0.01)
        return {"status_code": 200, "json": {"ok": True, "echo": payload}, "text": "OK"}


def _log(prefix: str, obj: Dict[str, Any]) -> None:
    # Keep the same logging format as the original module for compatibility
    print(prefix + json.dumps(obj, sort_keys=True))


__all__ = ["HttpClient", "_log"]
