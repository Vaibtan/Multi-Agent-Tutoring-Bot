import json
from typing import Any, Dict

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool


def classify_student_query(query: str) -> dict:
    math_keywords = [
        'calculate', 'solve', 'equation', 'algebra', 'geometry', 'calculus',
        'derivative', 'integral', 'function', 'graph', 'polynomial', 'trigonometry',
        'statistics', 'probability', 'matrix', 'vector', 'arithmetic', 'number'
    ]
    physics_keywords = [
        'force', 'energy', 'momentum', 'velocity', 'acceleration', 'mass',
        'gravity', 'electromagnetic', 'wave', 'quantum', 'relativity', 'thermodynamics',
        'optics', 'mechanics', 'newton', 'einstein', 'constant', 'formula'
    ]
    query_lower = query.lower()
    math_score = sum(1 for keyword in math_keywords if keyword in query_lower)
    physics_score = sum(1 for keyword in physics_keywords if keyword in query_lower)
    if math_score > physics_score and math_score > 0:
        return {
            "subject": "math",
            "confidence": min(math_score / 3, 1.0),
            "reasoning": f"Detected {math_score} math-related keywords"
        }
    elif physics_score > math_score and physics_score > 0:
        return {
            "subject": "physics", 
            "confidence": min(physics_score / 3, 1.0),
            "reasoning": f"Detected {physics_score} physics-related keywords"
        }
    else:
        return {
            "subject": "general",
            "confidence": 0.5,
            "reasoning": "No clear subject specialization detected"
        }

def provide_general_tutoring(query: str) -> dict:
    general_responses = {
        "study_tips": "Here are some effective study strategies: active recall, spaced repetition, and teaching others.",
        "motivation": "Remember that learning is a journey. Every expert was once a beginner!",
        "time_management": "Break study sessions into focused 25-50 minute blocks with short breaks.",
        "problem_solving": "When stuck on a problem, try breaking it into smaller parts and solving each step."
    }
    query_lower = query.lower()
    if any(word in query_lower for word in ['study', 'learn', 'tips']):
        return {"response": general_responses["study_tips"], "type": "study_tips"}
    elif any(word in query_lower for word in ['motivation', 'encourage', 'difficult']):
        return {"response": general_responses["motivation"], "type": "motivation"}
    elif any(word in query_lower for word in ['time', 'schedule', 'manage']):
        return {"response": general_responses["time_management"], "type": "time_management"}
    elif any(word in query_lower for word in ['stuck', 'problem', 'help']):
        return {"response": general_responses["problem_solving"], "type": "problem_solving"}
    else:
        return {
            "response": "I'm here to help! I can assist with math and physics questions, or provide general study guidance.",
            "type": "general_greeting"
        }

tutor_orchestrator = LlmAgent(
    name = "tutor_orchestrator",
    model = "gemini-2.0-flash",
    description = "Main tutoring coordinator that routes questions to specialized agents",
    instruction = """
    You are the main AI tutor coordinator. Your role is to:
    1. Welcome students warmly and assess their needs
    2. Classify their questions to route to appropriate specialists
    3. Coordinate between math and physics specialists
    4. Provide general study guidance and motivation
    5. Synthesize responses from specialist agents when needed
    6. Maintain a supportive and encouraging learning environment
    
    When you receive a student query:
    - First, classify the type of question
    - If it's math or physics specific, delegate to the appropriate specialist
    - If it's general, provide helpful study guidance
    - Always maintain an encouraging, educational tone
    - Follow up with additional learning suggestions when appropriate
    """,
    tools = [FunctionTool(classify_student_query), FunctionTool(provide_general_tutoring)],
    sub_agents = [
        # These will be imported and registered during system initialization
    ]
)