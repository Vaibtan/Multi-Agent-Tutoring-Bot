# Model Context Protocol compliant communication layer
import time
from typing import Any, Dict, Optional

from google.genai import types
from pydantic import BaseModel, Field


class MCPMessage(BaseModel):
    session_id: str
    message_type: str = Field(..., pattern="^(request|response|notification)$")
    payload: Dict[str, Any]
    metadata: Dict[str, str] = {}
    timestamp: float = Field(default_factory = lambda: time.time())

class MCPHandler:
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.sessions: Dict[str, Dict[str, Any]] = {}
        
    async def handle_message(self, message: MCPMessage) -> MCPMessage:
        handler_map = {
            "capability_negotiation": self.handle_capabilities,
            "tool_discovery": self.handle_tool_discovery,
            "context_update": self.handle_context_update
        }
        return await handler_map.get(message.message_type, self.default_handler)(message)

    async def handle_capabilities(self, message: MCPMessage) -> MCPMessage:
        capabilities = {
            "supported_formats": ["text", "json"],
            "max_context_length": 8192,
            "auth_requirements": ["bearer_token"]
        }
        return MCPMessage(session_id = message.session_id, \
            message_type = "response", payload = {"capabilities": capabilities})

    async def handle_tool_discovery(self, message: MCPMessage) -> MCPMessage:
        tools = await self.get_available_tools()
        return MCPMessage(session_id = message.session_id, \
            message_type = "response", payload = {"tools": tools})

    async def get_available_tools(self) -> list:
        return [tool.to_mcp_schema() for tool in self.agent.tools]