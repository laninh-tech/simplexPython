import ast
import math

class SafeEvalVisitor(ast.NodeVisitor):
    def __init__(self):
        self.functions = {
            'sqrt': math.sqrt,
            'abs': abs,
            'exp': math.exp,
            'log': math.log10,  # in C, log(x) is log10
            'ln': math.log,     # in C, ln(x) is log
            'root': lambda a, b: math.pow(b, 1.0 / a) if b >= 0 or int(a) % 2 != 0 else -math.pow(-b, 1.0 / a)
        }
        self.constants = {
            'pi': math.pi,
            'e': math.e
        }
        self.operators = {
            ast.Add: lambda x, y: x + y,
            ast.Sub: lambda x, y: x - y,
            ast.Mult: lambda x, y: x * y,
            ast.Div: lambda x, y: x / y,
            ast.Pow: lambda x, y: x ** y,
            ast.UAdd: lambda x: +x,
            ast.USub: lambda x: -x
        }

    def evaluate(self, node):
        if isinstance(node, ast.Expression):
            return self.evaluate(node.body)
        elif isinstance(node, ast.Constant):
            return float(node.value)
        elif isinstance(node, ast.Num):  # for compatibility with Python < 3.8
            return float(node.n)
        elif isinstance(node, ast.BinOp):
            op_type = type(node.op)
            if op_type not in self.operators:
                raise TypeError(f"Unacceptable binary operator: {op_type.__name__}")
            left = self.evaluate(node.left)
            right = self.evaluate(node.right)
            return self.operators[op_type](left, right)
        elif isinstance(node, ast.UnaryOp):
            op_type = type(node.op)
            if op_type not in self.operators:
                raise TypeError(f"Unacceptable unary operator: {op_type.__name__}")
            operand = self.evaluate(node.operand)
            return self.operators[op_type](operand)
        elif isinstance(node, ast.Name):
            name = node.id.lower()
            if name in self.constants:
                return self.constants[name]
            raise NameError(f"Undefined constant: {node.id}")
        elif isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name):
                raise TypeError("Function calls must be direct names")
            func_name = node.func.id.lower()
            if func_name not in self.functions:
                raise NameError(f"Undefined function: {node.func.id}")
            args = [self.evaluate(arg) for arg in node.args]
            return self.functions[func_name](*args)
        else:
            raise TypeError(f"Unacceptable expression node: {type(node).__name__}")

def eval_expression(expr_str: str) -> float:
    """Safe evaluation of mathematical expressions, mimicking simplexApp/menu/expression.c."""
    if not expr_str or not expr_str.strip():
        return 0.0
    try:
        expr_str = expr_str.replace('^', '**')  # standard caret to Python power conversion
        # Normalize Unicode dashes (en-dash and em-dash) from copy-pastes to standard hyphens
        expr_str = expr_str.replace('\u2013', '-').replace('\u2014', '-')
        tree = ast.parse(expr_str.strip(), mode='eval')
        visitor = SafeEvalVisitor()
        result = visitor.evaluate(tree)
        if math.isnan(result) or math.isinf(result):
            raise ValueError("Expression resulted in NaN or Infinity")
        return float(result)
    except Exception as e:
        raise ValueError(f"Could not parse expression '{expr_str}': {str(e)}")
