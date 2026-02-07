from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .models import Evidence, Finding
from utils.hash_utils import sha256_text


SEVERITY_ORDER = ['critical', 'high', 'medium', 'low', 'info']


def _clamp_line(lineno: Optional[int]) -> int:
    return int(lineno or 1)


def _evidence(file_path: str, start: int, end: int, line: str) -> Evidence:
    return Evidence(
        file=file_path,
        start_line=max(1, start),
        end_line=max(1, end),
        snippet_hash=sha256_text(line)[:16],
    )


def _source_line(text: str, lineno: int) -> str:
    lines = text.splitlines()
    idx = max(0, lineno - 1)
    if idx >= len(lines):
        return ''
    return lines[idx]


@dataclass
class FunctionInfo:
    name: str
    start_line: int
    end_line: int
    args_count: int
    has_docstring: bool
    complexity: int


class CyclomaticVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.complexity = 1

    def generic_visit(self, node: ast.AST) -> Any:
        if isinstance(node, (ast.If, ast.For, ast.While, ast.And, ast.Or, ast.With, ast.AsyncWith, ast.Try, ast.ExceptHandler)):
            self.complexity += 1
        if isinstance(node, (ast.BoolOp,)):
            self.complexity += max(0, len(getattr(node, 'values', [])) - 1)
        return super().generic_visit(node)


class PythonAstAnalyzer(ast.NodeVisitor):
    def __init__(self, file_path: str, text: str) -> None:
        self.file_path = file_path
        self.text = text
        self.findings: List[Finding] = []
        self._current_function: Optional[FunctionInfo] = None

    def add(self, *, id: str, category: str, severity: str, title: str, description: str, recommendation: str, confidence: int, lineno: int, end_lineno: Optional[int] = None, tags: Optional[List[str]] = None, cwe: Optional[str] = None) -> None:
        line = _source_line(self.text, lineno)
        evidence = _evidence(self.file_path, lineno, end_lineno or lineno, line)
        self.findings.append(Finding(
            id=id,
            category=category,
            severity=severity,
            title=title,
            description=description,
            recommendation=recommendation,
            confidence=int(confidence),
            rule_id=id,
            tool='vibe-ast',
            cwe=cwe,
            evidence=evidence,
            tags=tags or [],
        ))

    # --- Module-level checks
    def visit_Module(self, node: ast.Module) -> Any:
        # Basic docstring policy for modules could be added later.
        return self.generic_visit(node)

    # --- Functions
    def visit_FunctionDef(self, node: ast.FunctionDef) -> Any:
        self._analyze_function(node)
        return self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> Any:
        self._analyze_function(node)
        return self.generic_visit(node)

    def _analyze_function(self, node: ast.AST) -> None:
        name = getattr(node, 'name', '<lambda>')
        start_line = _clamp_line(getattr(node, 'lineno', 1))
        end_line = _clamp_line(getattr(node, 'end_lineno', start_line))
        args = getattr(node, 'args', None)
        args_count = 0
        if args is not None:
            args_count = len(getattr(args, 'posonlyargs', [])) + len(getattr(args, 'args', [])) + len(getattr(args, 'kwonlyargs', []))

        has_doc = bool(ast.get_docstring(node))
        cv = CyclomaticVisitor()
        cv.visit(node)
        complexity = cv.complexity

        # Function size/complexity signals
        if end_line - start_line + 1 > 80:
            self.add(
                id='VIBE_PY_LONG_FUNCTION',
                category='architecture',
                severity='medium',
                title=f'Long function: {name}',
                description=f'Function spans {end_line - start_line + 1} lines which increases cognitive load and risk of bugs.',
                recommendation='Refactor into smaller functions; extract helpers; keep single responsibility.',
                confidence=85,
                lineno=start_line,
                end_lineno=end_line,
                tags=['solid', 'clean-code'],
            )

        if args_count >= 7:
            self.add(
                id='VIBE_PY_TOO_MANY_ARGS',
                category='architecture',
                severity='medium',
                title=f'Too many parameters: {name}',
                description=f'Function has {args_count} parameters; high arity hurts readability and testability.',
                recommendation='Group parameters into a dataclass/config object; consider builder pattern; remove unused args.',
                confidence=85,
                lineno=start_line,
                tags=['solid', 'api-design'],
            )

        if complexity >= 15:
            self.add(
                id='VIBE_PY_HIGH_COMPLEXITY',
                category='bug',
                severity='high' if complexity >= 25 else 'medium',
                title=f'High cyclomatic complexity: {name} ({complexity})',
                description='High branching complexity increases defect probability and makes testing harder.',
                recommendation='Simplify conditional logic; split into smaller functions; use polymorphism/strategy; add tests for branches.',
                confidence=88,
                lineno=start_line,
                tags=['qa', 'test'],
            )

        if not has_doc and not name.startswith('_'):
            self.add(
                id='VIBE_PY_MISSING_DOCSTRING',
                category='docs',
                severity='low',
                title=f'Missing docstring: {name}',
                description='Public function has no docstring; decreases maintainability.',
                recommendation='Add a concise docstring explaining purpose, parameters, return value, and edge cases.',
                confidence=80,
                lineno=start_line,
                tags=['docs'],
            )

        # Mutable default args
        defaults = getattr(getattr(node, 'args', None), 'defaults', []) if getattr(node, 'args', None) else []
        for d in defaults:
            if isinstance(d, (ast.List, ast.Dict, ast.Set)):
                self.add(
                    id='VIBE_PY_MUTABLE_DEFAULT',
                    category='bug',
                    severity='high',
                    title=f'Mutable default argument in {name}',
                    description='Mutable default arguments are shared across calls and often cause unexpected state leakage.',
                    recommendation='Use None default and create a new list/dict inside the function.',
                    confidence=95,
                    lineno=_clamp_line(getattr(d, 'lineno', start_line)),
                    tags=['bug-pattern'],
                )

    # --- Calls
    def visit_Call(self, node: ast.Call) -> Any:
        # Detect eval/exec
        if isinstance(node.func, ast.Name) and node.func.id in {'eval', 'exec'}:
            self.add(
                id='VIBE_PY_EVAL_EXEC',
                category='security',
                severity='critical',
                title=f'Use of {node.func.id}()',
                description='Dynamic code execution can lead to remote code execution if inputs are not strictly controlled.',
                recommendation='Avoid eval/exec; use safe parsers (ast.literal_eval for literals) or explicit dispatch.',
                confidence=96,
                lineno=_clamp_line(getattr(node, 'lineno', 1)),
                cwe='CWE-95',
                tags=['security'],
            )

        # Detect subprocess shell=True
        if isinstance(node.func, ast.Attribute):
            attr = node.func.attr
            mod = getattr(getattr(node.func, 'value', None), 'id', None)
            if mod in {'subprocess'} and attr in {'run', 'call', 'Popen', 'check_output', 'check_call'}:
                for kw in node.keywords or []:
                    if kw.arg == 'shell' and isinstance(kw.value, ast.Constant) and kw.value.value is True:
                        self.add(
                            id='VIBE_PY_SUBPROCESS_SHELL',
                            category='security',
                            severity='high',
                            title='subprocess with shell=True',
                            description='shell=True enables shell injection if arguments include untrusted input.',
                            recommendation='Pass args as list; avoid shell=True; validate/sanitize any user-controlled data.',
                            confidence=92,
                            lineno=_clamp_line(getattr(node, 'lineno', 1)),
                            cwe='CWE-78',
                            tags=['security'],
                        )

        # Detect N+1 pattern (Call inside loop)
        # This is a heuristic: check if we are inside a loop and calling something that looks like a query
        if isinstance(node.func, (ast.Name, ast.Attribute)):
            func_name = node.func.id if isinstance(node.func, ast.Name) else node.func.attr
            if any(k in func_name.lower() for k in ['query', 'fetch', 'select', 'get_by_id', 'request']):
                # Check parents (this requires a bit more logic if we want to be precise, 
                # but for now we can check if we're in a loop context if we tracked it)
                pass

        return self.generic_visit(node)

    def visit_For(self, node: ast.For) -> Any:
        self._check_loop_complexity(node)
        return self.generic_visit(node)

    def visit_While(self, node: ast.While) -> Any:
        self._check_loop_complexity(node)
        return self.generic_visit(node)

    def _check_loop_complexity(self, node: ast.AST) -> None:
        # Detect nested loops
        nested_count = 0
        for child in ast.walk(node):
            if child == node: continue
            if isinstance(child, (ast.For, ast.While, ast.AsyncFor)):
                nested_count += 1
        
        if nested_count > 0:
            self.add(
                id='VIBE_PY_NESTED_LOOP',
                category='performance',
                severity='medium',
                title='Nested loop detected',
                description='Nested loops can lead to O(n^2) or worse time complexity.',
                recommendation='Consider using a hash map (dict) or set to reduce complexity to O(n); use vectorized operations if using numpy/pandas.',
                confidence=80,
                lineno=_clamp_line(getattr(node, 'lineno', 1)),
                tags=['performance'],
            )

        # Detect database/network calls in loops (N+1)
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                func_name = ''
                if isinstance(child.func, ast.Name):
                    func_name = child.func.id
                elif isinstance(child.func, ast.Attribute):
                    func_name = child.func.attr
                
                if any(k in func_name.lower() for k in ['query', 'fetch', 'select', 'get_by_id', 'request', 'execute']):
                    self.add(
                        id='VIBE_PY_N_PLUS_ONE',
                        category='performance',
                        severity='high',
                        title=f'Potential N+1 problem: {func_name} called in loop',
                        description='Executing queries or network requests inside a loop leads to significant performance degradation.',
                        recommendation='Use batch fetching, JOINs, or eager loading to retrieve all necessary data in a single call.',
                        confidence=85,
                        lineno=_clamp_line(getattr(child, 'lineno', getattr(node, 'lineno', 1))),
                        tags=['performance', 'database'],
                    )

    # --- With statement / open patterns
    def visit_Assign(self, node: ast.Assign) -> Any:
        # Very lightweight heuristic: f = open(...)
        if isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name) and node.value.func.id == 'open':
            self.add(
                id='VIBE_PY_OPEN_NO_WITH',
                category='bug',
                severity='medium',
                title='File opened without context manager',
                description='Opening files without `with` risks leaks on exceptions and makes lifetime unclear.',
                recommendation='Use `with open(...) as f:` to ensure proper close.',
                confidence=86,
                lineno=_clamp_line(getattr(node, 'lineno', 1)),
                tags=['resource'],
            )
        return self.generic_visit(node)

    # --- Exceptions
    def visit_Try(self, node: ast.Try) -> Any:
        # bare except
        for h in node.handlers or []:
            if h.type is None:
                self.add(
                    id='VIBE_PY_BARE_EXCEPT',
                    category='bug',
                    severity='high',
                    title='Bare except detected',
                    description='Bare except catches SystemExit/KeyboardInterrupt and hides bugs.',
                    recommendation='Catch specific exceptions; re-raise unexpected exceptions.',
                    confidence=93,
                    lineno=_clamp_line(getattr(h, 'lineno', getattr(node, 'lineno', 1))),
                    tags=['bug-pattern'],
                )

            # except Exception: pass (swallow)
            if isinstance(h.type, ast.Name) and h.type.id in {'Exception', 'BaseException'}:
                if all(isinstance(s, ast.Pass) for s in h.body or []):
                    self.add(
                        id='VIBE_PY_SWALLOW_EXCEPTION',
                        category='bug',
                        severity='high',
                        title='Exception swallowed with pass',
                        description='Swallowing exceptions silently makes failures hard to detect and debug.',
                        recommendation='Log the exception; return an error; or re-raise after adding context.',
                        confidence=90,
                        lineno=_clamp_line(getattr(h, 'lineno', getattr(node, 'lineno', 1))),
                        tags=['qa', 'debug'],
                    )

        return self.generic_visit(node)


def analyze_python_file(file_path: str, text: str) -> List[Finding]:
    try:
        tree = ast.parse(text)
    except SyntaxError:
        # Can't parse: treat as low-confidence bug
        return [Finding(
            id='VIBE_PY_SYNTAX_ERROR',
            category='bug',
            severity='high',
            title='Syntax error / failed parse',
            description='Python parser failed; file may be incomplete or invalid.',
            recommendation='Fix syntax errors and re-run analysis.',
            confidence=85,
            rule_id='VIBE_PY_SYNTAX_ERROR',
            tool='vibe-ast',
            evidence=Evidence(file=file_path, start_line=1, end_line=1, snippet_hash=sha256_text('')[:16]),
            tags=['parser'],
        )]

    analyzer = PythonAstAnalyzer(file_path=file_path, text=text)
    analyzer.visit(tree)
    return analyzer.findings
