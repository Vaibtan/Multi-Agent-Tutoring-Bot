import asyncio
import json
from typing import Any, Dict

from google.adk.agents import LlmAgent
from google.adk.runners import InMemoryRunner, Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import FunctionTool
from google.genai import types

from tools.history import (add_context, get_context, get_progress,
                           update_progress)

QUERY_CLASSIFICATION_INSTRUCTION: str = """
You are an expert query classifier. Your task is to analyze a student's query and determine its primary subject category.
The possible categories are: 'math', 'physics', or 'general'.
Respond with ONLY the category name in lowercase (e.g., "math", "physics", "general").
Do not add any other text, explanation, or punctuation. Just the single word.

Example:
Query: "Help me solve 2x + 5 = 10"
Response: math

Query: "What is Newton's second law?"
Response: physics

Query: "Any tips for studying?"
Response: general

Query: "Tell me about black holes and also calculate 5*5"
Response: physics
"""

classifier_agent = LlmAgent(name = "internal_query_classifier", \
    model = "gemini-2.5-flash-latest", instruction = QUERY_CLASSIFICATION_INSTRUCTION, tools = [])
classifier_session_service = InMemorySessionService()
classifier_runner = Runner(agent = classifier_agent, \
    session_service = classifier_session_service, app_name = "Multi-Agent Tutoring Bot")
classifier_sessions: Dict[str, str] = {}

async def run_classification_agent(query: str, user_id: str = "classifier_user") -> str:
    session_id: str
    if user_id not in classifier_sessions:
        session = await classifier_session_service.create_session(user_id = user_id, app_name = "Multi-Agent Tutoring Bot")
        classifier_sessions[user_id] = session.id; session_id = session.id
    else: session_id = classifier_sessions[user_id]
    response = ""
    async for event in classifier_runner.run_async(user_id = user_id, \
        session_id = session_id, new_message = types.Content(
                role = 'user', parts = [types.Part.from_text(text = query)])):
        if getattr(event, "content", None) and event.content.parts:
            for part in event.content.parts:
                if hasattr(part, 'text') and part.text: response += part.text
    classified_subject = response.strip().lower()
    if classified_subject not in ["math", "physics", "general"]:
        print(f"Warning: Classifier returned unexpected category: '{classified_subject}' for query: '{query}'. Defaulting to 'general'.")
        return "general"
    return classified_subject

async def classify_student_query(query: str) -> dict:
    try: subject = await run_classification_agent(query)
    except RuntimeError as e:
        print(f"Error running classification agent asynchronously: {e}. Falling back to keyword classification.")
        if any(kw in query.lower() for kw in ['math', 'solve', 'equation', 'calculate']): subject = "math"
        elif any(kw in query.lower() for kw in ['physics', 'force', 'energy', 'law']): subject = "physics"
        else: subject = "general"
    return {"subject": subject, "confidence": 1.0}

def tutoring_guidance(user_query_for_context: str) -> dict:
    return {
        "type": "general_tutoring_guidance_requested",
        "context": user_query_for_context
    }

tutor_orchestrator = LlmAgent(
    name = "tutor_orchestrator",
    model = "gemini-1.5-flash-latest",
    description = "Main AI tutoring coordinator. Classifies student queries and routes them to math or physics specialist agents, or handles general study advice directly.",
    instruction = """
    You are the main AI Tutor Orchestrator. Your primary responsibilities are:
    1.  Welcome and Understand: Warmly greet the student.
    2.  Classify Query: You MUST use the `classify_student_query` tool to determine if the student's question pertains to 'math', 'physics', or is 'general'.
    3.  State Classification and Intent:
        * If 'math': Respond with a message like "Okay, I'll connect you with our Math specialist. Classification: math".
        * If 'physics': Respond with a message like "Let me get our Physics expert for this. Classification: physics".
        * If 'general', or if the query is very clearly about study habits, motivation, how to learn, or how to use the tutoring system: You handle it directly. Provide helpful advice. Start your response with something like "Handling this general query:".
    4.  Synthesize and Present (for specialist responses later): When a specialist agent provides a response, present it clearly to the student. (This part of the instruction is more for a multi-turn scenario if you build that out).

    Your FIRST response to the user's query should be based on the classification.
    For 'math' or 'physics', your response should clearly indicate the subject so the system can route the original query.
    Example for math: "Okay, I'll ask our Math specialist to help with that. Classification: math"
    Example for physics: "Let's see what our Physics expert says. Classification: physics"
    Example for general: "Handling this general query: That's an interesting question! Here's some advice..."
    """,
    tools = [
        FunctionTool(classify_student_query), FunctionTool(tutoring_guidance), \
            FunctionTool(add_context), FunctionTool(get_context), \
                FunctionTool(update_progress), FunctionTool(get_progress)
    ]
)
