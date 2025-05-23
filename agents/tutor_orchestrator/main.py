import asyncio

from google.adk.runners import InMemoryRunner
from google.adk.sessions import InMemorySessionService

from agents.math_agent.agent import math_agent
from agents.physics_agent.agent import physics_agent
from agents.tutor_orchestrator.agent import tutor_orchestrator
from common.config import settings
from common.utils import extract_response_and_tools


class MultiAgentTutoringSystem:
    def __init__(self):
        self.settings = settings
        self.tutor = tutor_orchestrator
        self.math  = math_agent
        self.phys  = physics_agent
        self.runners = {
            self.tutor.name: InMemoryRunner(self.tutor),
            self.math.name : InMemoryRunner(self.math),
            self.phys.name : InMemoryRunner(self.phys),
        }
        self.session_service = InMemorySessionService()
        self._sessions: dict[str, str] = {}

    async def get_session_id(self, student_id: str) -> str:
        if student_id not in self._sessions:
            sess = await self.session_service.create_session(
                agent_name=self.tutor.name,
                user_id=student_id
            )
            self._sessions[student_id] = sess.id()
        return self._sessions[student_id]

    async def process_student_query(self, query: str, student_id: str = "student"):
        session_id = await self.get_session_id(student_id)
        classifier = self.runners[self.tutor.name]
        classify_evt = await classifier.run_function(
            user = student_id,
            session_id = session_id,
            tool_name = "classify_student_query",
            inputs = {"query": query}
        )
        subject = classify_evt["subject"]
        if subject == "math": runner = self.runners[self.math.name]
        elif subject == "physics": runner = self.runners[self.phys.name]
        else: runner = self.runners[self.tutor.name]
        events = runner.run_async(user = student_id, session_id = session_id, input = query)
        response_text, tools_used = await extract_response_and_tools(events)
        return {
            "response": response_text,
            "agent": runner.agent.name,
            "subject": subject,
            "tools_used": tools_used
        }

async def main():
    system = MultiAgentTutoringSystem()
    print("🎓 AI Tutor ready. Type ‘exit’ to quit.")
    while True:
        q = input("You: ").strip()
        if q.lower() in ("exit", "quit"):
            break
        result = await system.process_student_query(q, student_id="cli_user")
        print(f"\n[{result['agent']} | {result['subject']}]")
        print(result["response"])
        if result["tools_used"]:
            print("🔧 used:", ", ".join(result["tools_used"]))
        print()

if __name__ == "__main__": asyncio.run(main())
