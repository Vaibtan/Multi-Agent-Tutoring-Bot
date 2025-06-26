import asyncio
import random
import re
import string
import time
from typing import Any, AsyncGenerator, Dict, List

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from agents.math_agent.math_agent import math_agent
from agents.physics_agent.physics_agent import physics_agent
from agents.tutor_orchestrator.tutor_agent import tutor_orchestrator
from common.config import settings
from common.utils import extract_response_and_tools


class MultiAgentTutor:
    def __init__(self):
        self.settings = settings
        self.tutor = tutor_orchestrator
        self.math  = math_agent
        self.phys  = physics_agent
        self.session_service = InMemorySessionService() 
        self.runners = {
            self.tutor.name: Runner(agent = self.tutor, \
                session_service = self.session_service, app_name = "Multi-Agent Tutoring Bot"),
            self.math.name: Runner(agent = self.math, \
                session_service = self.session_service, app_name = "Multi-Agent Tutoring Bot"),
            self.phys.name : Runner(agent = self.phys, \
                session_service = self.session_service, app_name = "Multi-Agent Tutoring Bot"),
        }
        self.sessions: dict[str, str] = {}

    async def get_session_id(self, student_id: str, agent_for_session: str) -> str:
        session_key = f"{student_id}_{agent_for_session}"
        if session_key not in self.sessions:
            session = await self.session_service.create_session(user_id = student_id, app_name = "Multi-Agent Tutoring Bot")
            self.sessions[session_key] = session.id
        return self.sessions[session_key]

    async def process_student_query(self, query: str, student_id: str = "student") -> Dict[str, Any]:
        tutor_session_id = await self.get_session_id(student_id, self.tutor.name)
        print(f"Sending query to Tutor Orchestrator for classification: {self.tutor.name}")
        init_tutor_events = self.runners[self.tutor.name].run_async(user_id = student_id, \
            session_id = tutor_session_id, new_message = types.Content(
                role = 'user', parts = [types.Part.from_text(text = query)]))
        init_tutor_response, tutor_tools_used = await extract_response_and_tools(init_tutor_events)
        print(f"Tutor Orchestrator initial response: {init_tutor_response}")
        subject = "general"
        match = re.search(r"Classification:\s*(math|physics|general)", \
            init_tutor_response, re.IGNORECASE)
        if match: subject = match.group(1).lower()
        elif "handling this general query" in init_tutor_response.lower(): subject = "general"
        else:
            print(f"Could not reliably parse subject from tutor response. Defaulting to 'general'. Response was: {init_tutor_response}")
            return {
                "response": init_tutor_response,
                "agent": self.tutor.name,
                "subject": "general",
                "tools_used": tutor_tools_used,
                "student_id": student_id
            }
        print(f"[DEBUG] Query classified as: {subject} based on Tutor response.")
        chosen_agent: str
        final_response = init_tutor_response 
        final_tools = tutor_tools_used
        final_agent = self.tutor.name
        if subject == "math":
            chosen_agent = self.math.name
            print(f"[DEBUG] Routing original query to Math Agent: {self.math.name}")
            math_session_id = await self.get_session_id(student_id, self.math.name)
            math_events = self.runners[self.math.name].run_async(user_id = student_id, \
                session_id = math_session_id, new_message = types.Content(
                    role = 'user', parts = [types.Part.from_text(text = query)]))
            final_response, final_tools = await extract_response_and_tools(math_events)
            final_agent = self.math.name
        elif subject == "physics":
            chosen_agent = self.phys.name
            print(f"[DEBUG] Routing original query to Physics Agent: {self.phys.name}")
            phys_session_id = await self.get_session_id(student_id, self.phys.name)
            phys_events = self.runners[self.phys.name].run_async(user_id = student_id, \
                session_id = phys_session_id, new_message = types.Content(
                    role = 'user', parts = [types.Part.from_text(text = query)]))
            final_response, final_tools = await extract_response_and_tools(phys_events)
            final_agent = self.phys.name
        elif subject == "general":
            print(f"[DEBUG] Handled by Tutor Orchestrator as general query: {self.tutor.name}")
            pass 
        return {"response": final_response, "agent": final_agent, \
            "subject": subject, "tools_used": final_tools, "student_id": student_id}

class StreamingMultiAgentTutor(MultiAgentTutor):
    async def stream_student_query(self, *, query: str, \
        student_id: str = "student") -> AsyncGenerator[str, None]:
        tutor_session = await self.get_session_id(student_id, self.tutor.name)
        tutor_events = self.runners[self.tutor.name].run_async(
            user_id=student_id,
            session_id=tutor_session,
            new_message=types.Content(
                role="user", parts=[types.Part.from_text(text=query)]
            ),
        )
        tutor_response, tutor_tools = await extract_response_and_tools(tutor_events)
        subject = "general"
        if "classification:" in tutor_response.lower():
            import re
            m = re.search(r"classification:\s*(math|physics|general)", tutor_response, re.I)
            if m: subject = m.group(1).lower()
        elif "handling this general query" in tutor_response.lower(): subject = "general"

        async def yield_runner_chunks(runner_key: str):
            events = self.runners[runner_key].run_async(
                user_id = student_id,
                session_id = await self.get_session_id(student_id, runner_key),
                new_message = types.Content(role="user", parts = [types.Part.from_text(text = query)]),
            )
            async for ev in events:
                if getattr(ev, "content", None) and ev.content.parts: # type: ignore
                    for part in ev.content.parts: # type: ignore
                        if hasattr(part, "text") and part.text: yield part.text
        tools: List[str]
        if subject == "math":
            chunk_gen = yield_runner_chunks(self.math.name); tools = tutor_tools  
        elif subject == "physics":
            chunk_gen = yield_runner_chunks(self.phys.name); tools = tutor_tools
        else: 
            async def tutor_only(): yield tutor_response
            chunk_gen = tutor_only()
            tools = tutor_tools
        async for chunk in chunk_gen: yield chunk
        # After streaming language chunks, attach tools used (JSON list) so the
        # client can still surface them.  This matches common SSE patterns where
        # `event:` sets a custom event type that browsers can differentiate.
        yield "\n"
        if tools: import json; yield f"event: tools\ndata: {json.dumps(tools)}\n\n"

async def cli_main():
    if not settings.GEMINI_API_KEY:
        print("Error: GEMINI_API_KEY not found. Please set it in your .env file.")
        return     
    system = StreamingMultiAgentTutor()
    print("🎓 AI Tutor (Multi-Agent System with ADK) is ready. Type 'exit' or 'quit' to end.") 
    timestamp = int(time.time() * 1000)
    suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k = 6))
    student_id = f"cli_user_{timestamp}_{suffix}"
    while True:
        user_query = input("You: ").strip()
        if user_query.lower() in ["exit", "quit"]: print("Exiting AI Tutor. Goodbye!"); break
        if not user_query: continue
        try:
            result = await system.process_student_query(user_query, student_id = student_id)
            print(f"\nAI Tutor ({result['agent']} | Subject: {result['subject']}):")
            print(result['response'])
            if result.get('tools_used'):
                print(f"[Tools used by {result['agent']}: {', '.join(result['tools_used'])}]")
            print("-" * 30)
        except Exception as e:
            print(f"An error occurred: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    try: asyncio.run(cli_main())
    except KeyboardInterrupt: print("\nExiting AI Tutor...")