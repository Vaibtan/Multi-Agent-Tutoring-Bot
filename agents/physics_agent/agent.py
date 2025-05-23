import json

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool

from tools.constants import UniversalConstantsTool

physics_tool = UniversalConstantsTool()

def lookup_physics_constant(constant_name: str) -> dict: return \
    physics_tool.lookup_constant(constant_name) 

def lookup_physics_formula(formula_name: str) -> dict: return \
    physics_tool.lookup_formula(formula_name)

def get_physics_help(topic: str) -> dict:
    physics_concepts = {
        "mechanics": "Study of motion, forces, and energy in physical systems",
        "thermodynamics": "Study of heat, temperature, and energy transfer",
        "electromagnetism": "Study of electric and magnetic fields and their interactions",
        "optics": "Study of light, its properties, and behavior",
        "quantum": "Study of matter and energy at the atomic and subatomic level",
        "relativity": "Einstein's theories about space, time, and gravity"
    }
    topic_lower = topic.lower()
    for key, description in physics_concepts.items():
        if key in topic_lower or topic_lower in key:
            return {
                "status": "success",
                "topic": key,
                "description": description
            }
    return {
        "status": "info",
        "message": f"I can help with: {', '.join(physics_concepts.keys())}"
    }

physics_agent = LlmAgent(
    name = "physics_specialist",
    model = "gemini-2.0-flash",
    description = "Specialized physics tutor with access to constants and formulas",
    instruction = """
    You are an expert physics tutor. Your role is to:
    1. Explain physics concepts and laws clearly
    2. Look up physical constants when needed
    3. Provide relevant formulas and equations
    4. Solve physics problems step-by-step
    5. Connect theory to real-world applications
    6. Encourage scientific thinking and curiosity
    
    When you receive a physics question:
    - Identify the relevant physics principles
    - Look up any needed constants or formulas
    - Explain the concept before diving into calculations
    - Show step-by-step problem solving
    - Relate the answer to practical applications
    - Suggest further exploration topics
    """,
    tools = [FunctionTool(lookup_physics_constant), \
        FunctionTool(lookup_physics_formula), FunctionTool(get_physics_help)]
)
