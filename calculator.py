# server.py
from fastmcp import FastMCP
import sys
import logging
from safe_eval import safe_eval
from whitelist import _HAS_NUMPY

logger = logging.getLogger("Calculator")

# Fix UTF-8 encoding for Windows console
if sys.platform == "win32":
    sys.stderr.reconfigure(encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")

# Create MCP server
mcp = FastMCP("Calculator")

# Build tool description based on available modules
_CALC_DESCRIPTION = (
    "For mathematical calculation, always use this tool to calculate the result "
    "of a single Python expression. Just write the expression — no statements, "
    "imports, assignments, or semicolons. math, random"
    + (", numpy (or np)" if _HAS_NUMPY else "")
    + " are pre-imported and ready to use. "
    "Non-mathematical operations (import, open, eval, exec, os.system, "
    "__import__, etc.) are blocked. "
    "Example: math.sin(math.pi/2) + math.log(math.e)"
)


def _to_json(value):
    """Recursively convert numpy types to JSON-serializable Python types."""
    if _HAS_NUMPY:
        import numpy as np

        if isinstance(value, (np.integer,)):
            return int(value)
        if isinstance(value, (np.floating,)):
            return float(value)
        if isinstance(value, (np.bool_,)):
            return bool(value)
        if isinstance(value, (np.complexfloating,)):
            return [float(value.real), float(value.imag)]
        if isinstance(value, (np.ndarray,)):
            return _to_json(value.tolist())
        if isinstance(value, np.void):
            return None
        if isinstance(value, (bytes,)):
            return value.hex()
    if isinstance(value, (bytes,)):
        return value.hex()
    if isinstance(value, complex):
        return [value.real, value.imag]
    if isinstance(value, (tuple,)):
        return [_to_json(v) for v in value]
    if isinstance(value, (list,)):
        return [_to_json(v) for v in value]
    if isinstance(value, (dict,)):
        return {str(k): _to_json(v) for k, v in value.items()}
    return value


def _friendly_error(msg: str, expression: str) -> str:
    """Translate a technical error into guidance the AI can act on."""
    msg_lower = msg.lower()
    if "syntax error" in msg_lower:
        hint = ""
        if ";" in expression:
            hint = (
                "Semicolons are not allowed — you wrote multiple statements "
                "separated by ';'. Combine everything into a single expression. "
            )
        elif "=" in expression and not any(
            op in expression for op in ("==", "!=", "<=", ">=")
        ):
            hint = (
                "Variable assignment ('=') is not allowed — you cannot create "
                "variables. Instead, write everything inline as one expression. "
            )
        elif any(kw in expression for kw in ("import ", "from ")):
            hint = (
                "'import' is not allowed — all modules (math, random, numpy) "
                "are already pre-imported. Just use them directly. "
            )
        elif "\n" in expression.strip():
            hint = (
                "Multiple lines are not allowed — write a single expression. "
            )
        else:
            hint = (
                "Only a single expression is allowed — no statements, "
                "imports, semicolons, or assignments. "
            )
        return (
            f"{msg}. {hint}"
            "For example, instead of "
            "'import numpy as np; A = numpy.arange(1,26).reshape(5,5); "
            "numpy.linalg.matrix_rank(A)', just write: "
            "'numpy.linalg.matrix_rank(numpy.arange(1, 26).reshape(5, 5))'."
        )
    if "__import__" in msg:
        return (
            f"{msg}. Do NOT use __import__(). "
            "All modules (math, random, numpy) are pre-imported — "
            "just use them directly, e.g. 'numpy.array([1,2,3])'."
        )
    if "disallowed function call" in msg_lower:
        return (
            f"{msg}. This function is not allowed — only mathematical "
            "operations are permitted. Use functions from math, random, "
            "or numpy instead."
        )
    if "disallowed attribute" in msg_lower:
        return (
            f"{msg}. Only attributes of math, random, numpy (or np) "
            "are allowed. Use 'numpy.xxx' or 'math.xxx' directly."
        )
    if "disallowed method" in msg_lower:
        return (
            f"{msg}. Only safe array instance methods are allowed "
            "(e.g. .tolist(), .sum(), .T). Use numpy's functional API instead: "
            "'numpy.sum(arr)' rather than method calls on unknown objects."
        )
    if "undefined variable" in msg_lower:
        return (
            f"{msg}. Variables and imports are not supported — "
            "only math, random, numpy (or np) are pre-imported. "
            "Use them directly, e.g. 'numpy.array([1,2,3])'."
        )
    if "disallowed syntax" in msg_lower:
        return (
            f"{msg}. This syntax is not allowed in calculator expressions. "
            "You may have used a statement, lambda with unsupported features, "
            "or an operator like 'walrus (:=)' or f-string. "
            "Rewrite as a plain mathematical expression."
        )
    return msg


# Add calculator tool
@mcp.tool(description=_CALC_DESCRIPTION)
def calculator(python_expression: str) -> dict:
    try:
        raw = safe_eval(python_expression)
        result = _to_json(raw)
    except Exception as e:
        msg = _friendly_error(str(e), python_expression)
        logger.warning(f"Calculation failed: {python_expression}, error: {e}")
        return {"success": False, "error": msg}
    logger.info(f"Calculating formula: {python_expression}, result: {raw}")
    return {"success": True, "result": result}


# Start the server
if __name__ == "__main__":
    mcp.run(transport="stdio")
