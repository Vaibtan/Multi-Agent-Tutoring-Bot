from typing import Optional

import uvicorn
from fastapi import APIRouter, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from common.config import settings
from main import StreamingMultiAgentTutor

app = FastAPI(
    title = "Multi-Agent Tutoring Bot",
    description = "Interactive tutoring system with specialized math and physics agents",
    version = "0.0.1"
)

app.add_middleware(CORSMiddleware, allow_origins = settings.CORS_ORIGINS, \
    allow_credentials = True, allow_methods = ["*"], allow_headers = ["*"])

app.mount("/static", StaticFiles(directory = "web_interface/static"), name = "static")
templates = Jinja2Templates(directory = "web_interface/templates")
if not settings.GEMINI_API_KEY:
    print("FATAL ERROR: Gemini API key not found in environment variables")
    class DummyTutor:
        async def process_student_query(self, query: str, student_id: str):
            return {
                "response": "System is not configured: GEMINI_API_KEY is missing.",
                "agent": "system_error", "subject": "error", "tools_used": [], "student_id": student_id
            }
        async def stream_student_query(self, *, query: str, student_id: str):
            yield "System is not configured: GEMINI_API_KEY is missing."
    tutoring_system = DummyTutor()
else: tutoring_system = StreamingMultiAgentTutor()

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

@app.get("/", response_class = HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/chat", response_model = ChatResponse)
async def chat_endpoint(chat_message: ChatMessage):
    try:
        result = await tutoring_system.process_student_query(query = chat_message.message, \
            student_id = chat_message.student_id) # type: ignore
        return ChatResponse(response = result["response"], agent = result["agent"], \
            subject = result["subject"], tools_used = result["tools_used"], \
                student_id = chat_message.student_id) # type: ignore
    except Exception as e:
        print(f"Error processing chat message: {e}")
        raise HTTPException(status_code = 500, detail = f"Error processing your question: {str(e)}")

stream_router = APIRouter()
@stream_router.post("/chat/stream") 
async def chat_stream(message: str, student_id: str | None = "web_user") -> EventSourceResponse:
    # Stream LLM response via Server Sent Events
    async def event_publisher():
        try:
            async for chunk in tutoring_system.stream_student_query( # type: ignore
                query = message, student_id = student_id or "web_user"
            ):
                if chunk.strip(): yield f"data: {chunk}\n\n"
        except Exception as exc: f"data: Error: {str(exc)}\n\n"
    return EventSourceResponse(event_publisher())
app.include_router(stream_router, prefix = "/api")  

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy" if bool(settings.GEMINI_API_KEY) else "degraded",
        "agents": ["tutor_orchestrator", "math_specialist", "physics_specialist"],
        "message": "AI Tutoring System is running"
    }

@app.get("/api/agents/status")
async def agents_status():
    return { "tutor_orchestrator": {"status": "active", "port": settings.TUTOR_PORT} }

if __name__ == "__main__":
    print(f"Starting Uvicorn server on {settings.HOST}:{settings.TUTOR_PORT}")
    uvicorn.run("app:app", host = settings.HOST, port = settings.TUTOR_PORT, reload = True)

