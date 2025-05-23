import json

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool

from tools.calculator import CalculatorTool

calculator = CalculatorTool()

def calculate_expression(expression: str) -> dict: return calculator.calculate(expression)

def get_math_help(topic: str) -> dict:
    math_concepts = {
        "algebra": "Algebra involves working with variables and equations to solve for unknown values.",
        "geometry": "Geometry deals with shapes, sizes, positions, angles, and dimensions of objects.",
        "calculus": "Calculus is the study of continuous change, including derivatives and integrals.",
        "trigonometry": "Trigonometry studies relationships between angles and sides of triangles.",
        "statistics": "Statistics involves collecting, analyzing, and interpreting numerical data."
    }
    topic_lower: str = topic.lower()
    for key, description in math_concepts.items():
        if key in topic_lower or topic_lower in key:
            return {
                "status": "success",
                "topic": key,
                "description": description
            }
    return {
        "status": "info",
        "message": f"I can help with: {', '.join(math_concepts.keys())}"
    }

math_agent = LlmAgent(
    name = "math_specialist",
    model = "gemini-2.0-flash",
    description = "Specialized mathematics tutor capable of solving problems and explaining concepts",
    instruction = """
    You are an expert mathematics tutor. Your role is to:
    1. Solve mathematical problems step-by-step
    2. Explain mathematical concepts clearly
    3. Use the calculator tool for computations when needed
    4. Provide educational guidance and encouragement
    5. Break down complex problems into understandable steps
    
    When you receive a math problem:
    - Identify what type of problem it is
    - Explain the approach you'll take
    - Use tools when calculations are needed
    - Show your work step by step
    - Verify your answer when possible
    - Provide additional learning tips
    """,
    tools = [FunctionTool(calculate_expression), FunctionTool(get_math_help)]
)
