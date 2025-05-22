import ast
import math
import operator
from typing import Any, Dict, Union


class CalculatorTool:    
    operators: Dict[Any, Any] = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.BitXor: operator.xor,
        ast.USub: operator.neg,
    }
    
    functions: Dict[str, Any] = {
        'sin': math.sin,
        'cos': math.cos,
        'tan': math.tan,
        'sqrt': math.sqrt,
        'log': math.log,
        'exp': math.exp,
        'abs': abs,
        'round': round,
    }
    
    @staticmethod
    def evaluate_node(node):
        if isinstance(node, ast.Constant): return node.value
        elif isinstance(node, ast.BinOp):
            left = CalculatorTool.evaluate_node(node.left)
            right = CalculatorTool.evaluate_node(node.right)
            return CalculatorTool.operators[type(node.op)](left, right)
        elif isinstance(node, ast.UnaryOp):
            operand = CalculatorTool.evaluate_node(node.operand)
            return CalculatorTool.operators[type(node.op)](operand)
        elif isinstance(node, ast.Call):
            func_name = node.func.id
            if func_name in CalculatorTool.functions:
                args = [CalculatorTool.evaluate_node(arg) for arg in node.args]
                return CalculatorTool.functions[func_name](*args)
            else: raise ValueError(f"Unsupported function: {func_name}")
        else: raise ValueError(f"Unsupported operation: {type(node)}")

    def get_supported_functions(self) -> list: return list(CalculatorTool.functions.keys())

    def calculate(self, expression: str) -> Dict[str, Any]:
        try:
            tree = ast.parse(expression, mode = 'eval')        
            result = CalculatorTool.evaluate_node(tree.body)
            return {
                "status": "success",
                "result": result,
                "expression": expression
            }
        except (ValueError, SyntaxError, TypeError) as e:
            return {
                "status": "error",
                "error": str(e),
                "expression": expression
            }
