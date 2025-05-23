import asyncio
import os
import sys
from typing import Optional

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from agents.tutor_orchestrator.main import MultiAgentTutoringSystem
from common.config import settings

app = FastAPI(
    title = "AI Multi-Agent Tutoring System",
    description = "Interactive tutoring system with specialized math and physics agents",
    version = "1.0.0"
)

app.mount("/static", StaticFiles(directory = "web_interface/static"), name = "static")
templates = Jinja2Templates(directory = "web_interface/templates")
tutoring_system = MultiAgentTutoringSystem()

class ChatMessage(BaseModel):
    message: str
    student_id: Optional[str] = "web_user"

class ChatResponse(BaseModel):
    response: str
    agent: str
    subject: str
    tools_used: list[str]
    student_id: str
    error: Optional[str] = None

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(chat_message: ChatMessage):
    try:
        result = await tutoring_system.process_student_query(query = chat_message.message, \
            student_id = chat_message.student_id)
        return ChatResponse(response = result["response"], agent = result["agent"], \
            subject = result["subject"], tools_used = result["tools_used"], \
                student_id = chat_message.student_id)
    except Exception as e:
        print(f"Error processing chat message: {e}")
        raise HTTPException(
            status_code = 500, 
            detail = f"Error processing your question: {str(e)}"
        )

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "agents": ["tutor_orchestrator", "math_specialist", "physics_specialist"],
        "message": "AI Tutoring System is running"
    }

@app.get("/api/agents/status")
async def agents_status():
    return {
        "tutor_orchestrator": {"status": "active", "port": settings.TUTOR_PORT},
        "math_specialist": {"status": "active", "port": settings.MATH_PORT},
        "physics_specialist": {"status": "active", "port": settings.PHYSICS_PORT}
    }

if __name__ == "__main__":
    uvicorn.run("app:app", host = settings.HOST, port = settings.TUTOR_PORT, reload = True, log_level = "info")
