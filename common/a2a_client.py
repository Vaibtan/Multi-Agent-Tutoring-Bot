from typing import Any, Dict, Optional

import httpx


class A2AClient:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.client = httpx.AsyncClient()
    
    async def run_agent(self, target_agent: str, user_input: str, \
        port: int, session_id: Optional[str] = None) -> Dict[str, Any]:
        url = f"{self.base_url}:{port}/run"
        payload = {
            "input": user_input,
            "session_id": session_id or f"default_{target_agent}"
        }
        try:
            response = await self.client.post(url, json = payload, \
                headers = {"Content-Type": "application/json"}
            )
            response.raise_for_status(); return response.json()
        except httpx.RequestError as e:
            return {
                "error": f"Failed to connect to {target_agent}: {str(e)}",
                "status": "connection_error"
            }
        except httpx.HTTPStatusError as e:
            return {
                "error": f"HTTP error from {target_agent}: {e.response.status_code}",
                "status": "http_error"
            }
    
    async def get_agent_info(self, port: int = 8000) -> Dict[str, Any]:
        url = f"{self.base_url}:{port}/.well-known/agent.json"
        try:
            response = await self.client.get(url); response.raise_for_status()
            return response.json()
        except Exception as e: return {"error": str(e), "status": "info_error"}
    
    async def close(self): await self.client.aclose()
