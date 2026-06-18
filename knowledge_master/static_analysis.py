"""Static analysis — extract import graphs, symbols, and call relationships from code."""

import ast
import os
from pathlib import Path


def extract_python_graph(file_path: str) -> dict:
    """Extract imports, exports (top-level functions/classes), and calls from a Python file."""
    try:
        source = Path(file_path).read_text(errors="ignore")
        tree = ast.parse(source)
    except (SyntaxError, ValueError):
        return {"imports": [], "exports": [], "calls": [], "path": file_path}

    imports = []
    exports = []
    calls = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append({"module": alias.name, "alias": alias.asname, "names": []})
        elif isinstance(node, ast.ImportFrom):
            imports.append({
                "module": node.module or "",
                "names": [a.name for a in node.names],
                "level": node.level,
            })
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.col_offset == 0:  # top-level function
                exports.append({"name": node.name, "type": "function", "line": node.lineno})
        elif isinstance(node, ast.ClassDef):
            if node.col_offset == 0:  # top-level class
                bases = [_node_name(b) for b in node.bases]
                exports.append({"name": node.name, "type": "class", "line": node.lineno, "bases": bases})

    return {"imports": imports, "exports": exports, "calls": calls, "path": file_path}


def resolve_import(module: str, level: int, source_file: str, repo_root: str) -> str | None:
    """Resolve an import to a file path within the repo."""
    if level > 0:
        # Relative import: go up `level` directories from source file's package
        source_dir = Path(os.path.join(repo_root, source_file)).parent
        for _ in range(level - 1):
            source_dir = source_dir.parent
        parts = module.split(".") if module else []
        candidate = source_dir / Path(*parts) if parts else source_dir
    else:
        # Absolute import — check if it's a local module
        parts = module.split(".")
        candidate = Path(repo_root) / Path(*parts)

    # Try as module.py or package/__init__.py
    as_file = str(candidate) + ".py"
    as_pkg = str(candidate / "__init__.py")

    if os.path.exists(as_file):
        return os.path.relpath(as_file, repo_root)
    if os.path.exists(as_pkg):
        return os.path.relpath(as_pkg, repo_root)

    return None


def build_import_graph(repo_path: str, graph):
    """Walk a repo, extract Python imports, store as IMPORTS edges between File nodes."""
    repo_path = str(Path(repo_path).resolve())
    repo_name = Path(repo_path).name
    py_files = list(Path(repo_path).rglob("*.py"))
    py_files = [f for f in py_files if not any(
        p in f.parts for p in (".venv", "venv", "node_modules", "__pycache__", ".git", "site-packages")
    )]

    file_exports = {}  # relative_path -> [exported symbols]
    file_imports = {}  # relative_path -> [import info]

    # Pass 1: collect exports and imports
    for py_file in py_files:
        relative = os.path.relpath(str(py_file), repo_path)
        result = extract_python_graph(str(py_file))
        file_exports[relative] = result["exports"]
        file_imports[relative] = result["imports"]

        # Store Function/Class nodes
        for export in result["exports"]:
            node_type = "Function" if export["type"] == "function" else "Class"
            graph.query(
                f"MERGE (s:{node_type} {{name: $name, file: $file, repo: $repo}}) SET s.line = $line",
                params={"name": export["name"], "file": relative, "repo": repo_name, "line": export["line"]},
            )
            # Link symbol to file
            graph.query(
                f"""MATCH (s:{node_type} {{name: $name, file: $file}}), (d:Document {{path: $file}})
                    MERGE (s)-[:DEFINED_IN]->(d)""",
                params={"name": export["name"], "file": relative},
            )

    # Pass 2: resolve imports to file paths, create IMPORTS edges
    edges_created = 0
    for source_file, imports in file_imports.items():
        for imp in imports:
            module = imp.get("module", "")
            level = imp.get("level", 0)
            names = imp.get("names", [])

            if module:
                # from module import X  or  import module
                target_file = resolve_import(module, level, source_file, repo_path)
                if target_file and target_file in file_exports:
                    graph.query(
                        """MERGE (src:Document {path: $src})
                           MERGE (dst:Document {path: $dst})
                           MERGE (src)-[:IMPORTS {names: $names}]->(dst)""",
                        params={"src": source_file, "dst": target_file, "names": names},
                    )
                    edges_created += 1
            elif level > 0 and names:
                # from . import module1, module2 — each name is a sibling module
                for name in names:
                    target_file = resolve_import(name, level, source_file, repo_path)
                    if target_file and target_file in file_exports:
                        graph.query(
                            """MERGE (src:Document {path: $src})
                               MERGE (dst:Document {path: $dst})
                               MERGE (src)-[:IMPORTS {names: $imp_names}]->(dst)""",
                            params={"src": source_file, "dst": target_file, "imp_names": [name]},
                        )
                        edges_created += 1

    return {"files_analyzed": len(py_files), "import_edges": edges_created, "symbols": sum(len(v) for v in file_exports.values())}


def _node_name(node) -> str:
    """Get string name from an AST node."""
    if isinstance(node, ast.Name):
        return node.id
    elif isinstance(node, ast.Attribute):
        return f"{_node_name(node.value)}.{node.attr}"
    return ""
