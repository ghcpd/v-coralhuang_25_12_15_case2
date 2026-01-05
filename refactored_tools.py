"""
Refactored tool implementation with shared base classes to eliminate duplication.

This module provides:
- InputValidator: Centralized validation logic
- PayloadBuilder: Consistent payload construction
- BaseTool: Common tool functionality
- ToolA, ToolB, ToolC: Refactored tool implementations
"""

import json
import time
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class HttpClient:
    """Simulated HTTP client for making POST requests."""
    
    def post(self, url: str, payload: Dict[str, Any], timeout_s: float = 10.0) -> Dict[str, Any]:
        """Send a POST request to the given URL.
        
        Args:
            url: The endpoint URL
            payload: The request payload
            timeout_s: Request timeout in seconds
            
        Returns:
            Response dictionary with status_code, json, and text
        """
        # Fake transport (simulated response)
        time.sleep(0.01)
        return {"status_code": 200, "json": {"ok": True, "echo": payload}, "text": "OK"}


def _log(prefix: str, obj: Dict[str, Any]) -> None:
    """Log a message with JSON object."""
    print(prefix + json.dumps(obj, sort_keys=True))


class InputValidator:
    """Centralized validation logic for tool inputs."""
    
    @staticmethod
    def validate_user_id(user_id: str, param_name: str = "user_id") -> Optional[str]:
        """
        Validate user_id parameter.
        
        Args:
            user_id: The user ID to validate
            param_name: The name to use in error message
            
        Returns:
            Error message string if invalid, None if valid
        """
        if not user_id or (isinstance(user_id, str) and user_id == ""):
            return f"{param_name} is required"
        return None
    
    @staticmethod
    def validate_query(query: str) -> Optional[str]:
        """
        Validate query parameter.
        
        Args:
            query: The query string to validate
            
        Returns:
            Error message string if invalid, None if valid
        """
        if query is None or query == "":
            return "query is required"
        if not isinstance(query, str):
            return "query must be a string"
        return None
    
    @staticmethod
    def validate_limit(limit: int, min_value: int = 1) -> Optional[str]:
        """
        Validate limit parameter.
        
        Args:
            limit: The limit value to validate
            min_value: Minimum allowed value (default: 1)
            
        Returns:
            Error message string if invalid, None if valid
        """
        if limit < min_value:
            return f"limit must be >= {min_value}"
        return None


class PayloadBuilder:
    """Constructs request payloads with consistent formatting."""
    
    @staticmethod
    def build(
        user_id: str,
        query: str,
        limit: int,
        tool_name: str,
        custom_fields: Optional[Dict[str, Any]] = None,
        strip_query: bool = True,
        query_key: str = "query",
    ) -> Dict[str, Any]:
        """
        Build a request payload.
        
        Args:
            user_id: User ID (will use camelCase key userId)
            query: Query string
            limit: Limit value
            tool_name: Tool identifier (e.g., "A", "B", "C")
            custom_fields: Additional fields to include in payload
            strip_query: Whether to strip whitespace from query
            query_key: Key name for query field in payload (default: "query", can be "q")
            
        Returns:
            Request payload dictionary
        """
        query_value = query.strip() if strip_query else query
        
        payload = {
            "userId": user_id,
            query_key: query_value,
            "limit": limit,
            "tool": tool_name,
        }
        
        if custom_fields:
            payload.update(custom_fields)
        
        return payload


class BaseTool(ABC):
    """Abstract base class for all tools."""
    
    def __init__(self, client: HttpClient, base_url: str):
        """
        Initialize tool with HTTP client and base URL.
        
        Args:
            client: HttpClient instance
            base_url: Base URL for requests
        """
        self.client = client
        self.base_url = base_url
    
    @abstractmethod
    def get_validation_rules(self) -> Dict[str, Any]:
        """Get validation configuration for this tool.
        
        Returns:
            Dict with keys: min_limit, strip_query, query_key
        """
        pass
    
    @abstractmethod
    def get_tool_name(self) -> str:
        """Get the tool name identifier."""
        pass
    
    def _validate_inputs(
        self,
        user_id: str,
        query: str,
        limit: int,
        min_limit: int = 1,
    ) -> Optional[Dict[str, Any]]:
        """
        Validate tool inputs.
        
        Args:
            user_id: User ID
            query: Query string
            limit: Limit value
            min_limit: Minimum allowed limit
            
        Returns:
            Error dict if validation fails, None if valid
        """
        error = InputValidator.validate_user_id(user_id)
        if error:
            return {"ok": False, "error": error}
        
        error = InputValidator.validate_query(query)
        if error:
            return {"ok": False, "error": error}
        
        error = InputValidator.validate_limit(limit, min_value=min_limit)
        if error:
            return {"ok": False, "error": error}
        
        return None
    
    def run(self, user_id: str, query: str, limit: int = 10, timeout_s: float = 10.0) -> Dict[str, Any]:
        """
        Execute the tool.
        
        Args:
            user_id: User ID
            query: Search query
            limit: Result limit
            timeout_s: Request timeout
            
        Returns:
            Response dict with ok, data/error, and status_code
        """
        rules = self.get_validation_rules()
        
        # Validate inputs
        validation_error = self._validate_inputs(
            user_id,
            query,
            limit,
            min_limit=rules.get("min_limit", 1),
        )
        if validation_error:
            return validation_error
        
        # Build payload
        payload = PayloadBuilder.build(
            user_id=user_id,
            query=query,
            limit=limit,
            tool_name=self.get_tool_name(),
            strip_query=rules.get("strip_query", True),
            query_key=rules.get("query_key", "query"),
        )
        
        # Log and send request
        url = self.base_url + "/search"
        _log(f"[{self.__class__.__name__}] request=", {"url": url, "payload": payload})
        resp = self.client.post(url, payload, timeout_s=timeout_s)
        
        # Handle response
        if resp.get("status_code") != 200:
            return {
                "ok": False,
                "error": f"HTTP {resp.get('status_code')}",
                "raw": resp,
            }
        
        return {"ok": True, "data": resp.get("json"), "status_code": resp.get("status_code")}


class ToolA(BaseTool):
    """Tool A - refactored with stricter validation."""
    
    def get_tool_name(self) -> str:
        return "A"
    
    def get_validation_rules(self) -> Dict[str, Any]:
        """ToolA uses strict validation: limit must be > 0, query is stripped."""
        return {
            "min_limit": 1,      # limit > 0
            "strip_query": True,
            "query_key": "query",
        }


class ToolB(BaseTool):
    """Tool B - refactored with corrected limit validation."""
    
    def get_tool_name(self) -> str:
        return "B"
    
    def get_validation_rules(self) -> Dict[str, Any]:
        """ToolB now uses consistent limit validation: limit >= 1 (matching ToolA behavior)."""
        return {
            "min_limit": 1,      # Corrected: was allowing 0, now consistent with others
            "strip_query": False,  # Original behavior: doesn't strip
            "query_key": "query",
        }


class ToolC(BaseTool):
    """Tool C - refactored with consistent validation."""
    
    def get_tool_name(self) -> str:
        return "C"
    
    def get_validation_rules(self) -> Dict[str, Any]:
        """ToolC now uses consistent limit validation: limit >= 1 (matching ToolA/B behavior)."""
        return {
            "min_limit": 1,      # Corrected: was rejecting 0, now consistent
            "strip_query": True,
            "query_key": "q",    # Original behavior: uses "q" as key
        }
