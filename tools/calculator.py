import ast
import math
import operator
from typing import Any, Dict, List, Union


class CalculatorTool:    
    operators: Dict[Any, Any] = {
        ast.Add: lambda a, b: a + b,
        ast.Sub: lambda a, b: a - b,
        ast.Mult: lambda a, b: a * b,
        ast.Div: lambda a, b: a / b,
        ast.Pow: lambda a, b: a ** b,
        ast.BitXor: lambda a, b: a ^ b,
        ast.USub: lambda a: -a,
    }
    
    functions: Dict[str, Any] = {
        'sin': math.sin,
        'cos': math.cos,
        'tan': math.tan,
        'sqrt': math.sqrt,
        'log': math.log,
        'log10': math.log10,
        'log2': math.log2,
        'exp': math.exp,
        'abs': abs,
        'round': round,
        'factorial': math.factorial,
        'pi': lambda: math.pi,
        'e': lambda: math.e,
    }
    
    @staticmethod
    def evaluate_node(cls, node: ast.AST) -> Union[int, float]:
        if isinstance(node, ast.Constant): return node.value
        elif isinstance(node, ast.BinOp):
            left = CalculatorTool.evaluate_node(node.left)
            right = CalculatorTool.evaluate_node(node.right)
            op_type = type(node.op)
            if op_type in CalculatorTool.operators: return CalculatorTool.\
                operators[op_type](left, right)
            raise ValueError(f"Unsupported binary operator: {op_type.__name__}")
        elif isinstance(node, ast.UnaryOp):
            operand = CalculatorTool.evaluate_node(node.operand)
            op_type = type(node.op)
            if op_type in CalculatorTool.operators: return CalculatorTool.\
                operators[op_type](operand)
            raise ValueError(f"Unsupported unary operator: {op_type.__name__}")
        elif isinstance(node, ast.Call):
            func_node = node.func
            if isinstance(func_node, ast.Name): func_name = func_node.id
            elif isinstance(func_node, ast.Attribute): func_name = func_node.attr
            else: raise ValueError(f"Unsupported function call structure: {ast.dump(node)}")
            if func_name not in CalculatorTool.functions:
                raise ValueError(f"Unsupported function: {func_name}")
            args = [CalculatorTool.evaluate_node(arg) for arg in node.args]
            return CalculatorTool.functions[func_name](*args)
        elif isinstance(node, ast.Name) and node.id in ['pi', 'e']:
             if node.id in CalculatorTool.functions: return CalculatorTool.functions[node.id]()
        raise ValueError(f"Unsupported AST node type: {type(node).__name__}")

    @classmethod
    def get_supported_functions(cls) -> List[str]: return list(cls.functions.keys())

    @classmethod
    def calculate(cls, expr: str) -> Dict[str, Any]:
        try:
            processed_expr = expr.lower().replace('^', '**').replace(' ', '')
            if not processed_expr: raise ValueError("Expression cannot be empty.")
            parsed_ast = ast.parse(processed_expr, mode = 'eval') 
            if not isinstance(parsed_ast, ast.Expression) or not parsed_ast.body:
                raise SyntaxError("Invalid expression structure.")       
            result = cls.evaluate_node(parsed_ast.body)
            return {
                "status": "success",
                "result": result,
                "expression": expr
            }
        except (ValueError, SyntaxError, TypeError, ZeroDivisionError) as e:
            return {
                "status": "error",
                "error": str(e),
                "expression": expr
            }
        except Exception as e:
            return {
                "status": "error",
                "error": f"An unexpected error occurred during calculation: {str(e)}",
                "expression": expr
            }
