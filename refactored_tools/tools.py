from .base import BaseTool
from .client import HttpClient


class ToolA(BaseTool):
    TOOL_NAME = "A"

    def __init__(self, client: HttpClient, base_url: str):
        super().__init__(client, base_url)


class ToolB(BaseTool):
    TOOL_NAME = "B"

    def __init__(self, client: HttpClient, base_url: str):
        super().__init__(client, base_url)


class ToolC(BaseTool):
    TOOL_NAME = "C"

    def __init__(self, client: HttpClient, base_url: str):
        super().__init__(client, base_url)
