"""
Safe expression evaluator using AST whitelist parsing.

Replaces bare eval() to prevent sandbox escape attacks.
All whitelist data lives in whitelist.py; this module contains only logic.
"""

import ast
from whitelist import (
    ALLOWED_NODES,
    ALLOWED_MODULES,
    SAFE_BUILTINS,
    SAFE_METHODS,
    MODULE_ALIASES,
)

# ==================================================================
# Internal helpers
# ==================================================================


def _resolve_attr_path(node):
    """Resolve a chain of ast.Attribute nodes into a dotted path string.

    e.g., numpy.fft.fft  ->  'numpy.fft.fft'
    Returns the path string, or None if the base is not a Name.
    """
    parts = []
    current = node
    while isinstance(current, ast.Attribute):
        parts.append(current.attr)
        current = current.value
    if not isinstance(current, ast.Name):
        return None
    parts.append(current.id)
    parts.reverse()
    return ".".join(parts)


def _validate_attribute(path):
    """Validate an attribute path against the module/submodule whitelist.

    Rules:
      - Root must be a known module (or alias) in ALLOWED_MODULES.
      - Every prefix before the leaf must be a known submodule.
      - The leaf must be in its parent's whitelist.
    """
    parts = path.split(".")

    # Resolve alias (e.g. np -> numpy)
    root = MODULE_ALIASES.get(parts[0], parts[0])

    # Reconstruct path with resolved root
    resolved_parts = [root] + parts[1:]
    resolved_path = ".".join(resolved_parts)

    if root not in ALLOWED_MODULES:
        raise ValueError(f"Disallowed attribute access: {path}")

    if len(resolved_parts) == 1:
        return  # bare module name is fine as a value

    if len(resolved_parts) == 2:
        # Check if leaf is either a function of the root module,
        # or the full path is a known submodule name.
        if (
            resolved_parts[1] not in ALLOWED_MODULES[root]
            and resolved_path not in ALLOWED_MODULES
        ):
            raise ValueError(f"Disallowed attribute: {path}")
        return

    # 3+ segments: every intermediate prefix must be a known submodule
    for i in range(1, len(resolved_parts)):
        subpath = ".".join(resolved_parts[: i + 1])
        if i < len(resolved_parts) - 1:
            if subpath not in ALLOWED_MODULES:
                raise ValueError(
                    f"Disallowed attribute: {subpath} (not a known submodule)"
                )
        else:
            parent = ".".join(resolved_parts[:i])
            if (
                parent not in ALLOWED_MODULES
                or resolved_parts[i] not in ALLOWED_MODULES[parent]
            ):
                raise ValueError(f"Disallowed attribute: {path}")


def _validate_ast(node, local_vars=frozenset()):
    """Recursively validate AST nodes against the whitelist to prevent sandbox escape."""
    node_type = type(node)

    if node_type not in ALLOWED_NODES:
        raise ValueError(f"Disallowed syntax: {node_type.__name__}")

    # ---- Attribute nodes ----
    if isinstance(node, ast.Attribute):
        path = _resolve_attr_path(node)
        if path is not None and path.split(".")[0] in ALLOWED_MODULES:
            # Base is a known module → math.sin, numpy.fft.fft
            _validate_attribute(path)
        else:
            # Base is not a module → validate the base chain first so errors
            # point to the real problem (e.g. __import__), then check the leaf.
            for child in ast.iter_child_nodes(node):
                _validate_ast(child, local_vars)
            if node.attr not in SAFE_METHODS:
                raise ValueError(f"Disallowed method: .{node.attr}()")
            return  # already recursed manually

    # ---- Call nodes ----
    if isinstance(node, ast.Call):
        func = node.func
        if isinstance(func, ast.Name):
            if func.id not in SAFE_BUILTINS:
                raise ValueError(f"Disallowed function call: {func.id}")
        elif isinstance(func, ast.Attribute):
            pass  # Already validated by the Attribute check above
        elif isinstance(func, ast.Lambda):
            pass  # Lambda is validated above
        elif isinstance(func, ast.Call):
            pass  # whitelisted callable-returning function (e.g. numpy.vectorize)
        else:
            raise ValueError("Disallowed call form")

    # ---- Name nodes ----
    if isinstance(node, ast.Name):
        if node.id not in SAFE_BUILTINS and node.id not in local_vars:
            raise ValueError(f"Undefined variable: {node.id}")

    # ---- Lambda (parameters are local scope, body validated recursively) ----
    if isinstance(node, ast.Lambda):
        new_locals = set(local_vars)
        for arg in node.args.args:
            new_locals.add(arg.arg)
        if node.args.vararg:
            new_locals.add(node.args.vararg.arg)
        if node.args.kwarg:
            new_locals.add(node.args.kwarg.arg)
        _validate_ast(node.body, frozenset(new_locals))
        return

    # ---- Comprehensions (iteration variables are local scope) ----
    if isinstance(node, (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)):
        new_locals = set(local_vars)
        for gen in node.generators:
            _collect_names(gen.target, new_locals)
            for if_clause in gen.ifs:
                _validate_ast(if_clause, frozenset(new_locals))
            _validate_ast(gen.iter, local_vars)
        if isinstance(node, ast.ListComp):
            _validate_ast(node.elt, frozenset(new_locals))
        elif isinstance(node, ast.SetComp):
            _validate_ast(node.elt, frozenset(new_locals))
        elif isinstance(node, ast.DictComp):
            _validate_ast(node.key, frozenset(new_locals))
            _validate_ast(node.value, frozenset(new_locals))
        elif isinstance(node, ast.GeneratorExp):
            _validate_ast(node.elt, frozenset(new_locals))
        return

    # ---- Recurse into children ----
    for child in ast.iter_child_nodes(node):
        _validate_ast(child, local_vars)


def _collect_names(node, names_set):
    """Collect variable names from an assignment target (for comprehension iteration vars)."""
    if isinstance(node, ast.Name):
        names_set.add(node.id)
    elif isinstance(node, (ast.Tuple, ast.List)):
        for elt in node.elts:
            _collect_names(elt, names_set)


# ==================================================================
# Public API
# ==================================================================


def safe_eval(expression: str):
    """Safely evaluate a mathematical expression using AST whitelist parsing.

    Args:
        expression: A mathematical expression string.

    Returns:
        The computed result.

    Raises:
        TypeError: Input is not a string.
        ValueError: Expression is empty, has syntax errors, or contains
                    disallowed operations.
    """
    if not isinstance(expression, str):
        raise TypeError("Expression must be a string")
    if not expression.strip():
        raise ValueError("Expression is empty")

    try:
        tree = ast.parse(expression.strip(), mode="eval")
    except SyntaxError as e:
        raise ValueError(f"Syntax error: {e}")

    _validate_ast(tree)

    code = compile(tree, "<calculator>", "eval")
    # Merge safe builtins into globals so that lambdas / nested scopes
    # can access them via closure.  Top-level names resolve from globals
    # (locals is empty).  NameNode check in _validate_ast still applies.
    safe_globals = dict(SAFE_BUILTINS)
    safe_globals["__builtins__"] = {
        "__import__": __import__,
        "isinstance": isinstance,
        "issubclass": issubclass,
    }
    return eval(code, safe_globals, {})
