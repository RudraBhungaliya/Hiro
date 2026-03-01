import requests
import json
import ast
import sys
from pathlib import Path


def read_file(filepath):
    """Read a .py file and return its contents as a string."""
    path = Path(filepath)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {filepath}")

    if path.suffix != ".py":
        raise ValueError(f"Only .py files supported right now: {filepath}")

    return path.read_text()


def extract_with_ast(code):
    """
    Using Python's built-in AST to extract facts directly from code.
    Returns classes, methods, dependencies, imports, and function calls.
    """
    tree = ast.parse(code)
    facts = {
        "classes": [],
        "imports": [],
        "functions": [],
        "calls": []
    }

    all_class_names = [
        node.name for node in ast.walk(tree)
        if isinstance(node, ast.ClassDef)
    ]

    method_names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    method_names.add(item.name)

    # Collecting all top level function names first
    all_function_names = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            if node.name not in method_names and node.name != "__init__":
                all_function_names.append(node.name)

    for node in ast.walk(tree):

        if isinstance(node, ast.ClassDef):
            methods = []
            dependencies = set()

            for item in node.body:
                if isinstance(item, ast.FunctionDef):

                    if item.name != "__init__":
                        methods.append(item.name)

                    if item.name == "__init__":
                        for arg in item.args.args:
                            arg_name = arg.arg.lower()
                            if arg_name == "self":
                                continue
                            for class_name in all_class_names:
                                if class_name == node.name:
                                    continue
                                class_lower = class_name.lower()
                                stripped = class_lower.replace("service", "").replace("manager", "").replace("repository", "")
                                if (arg_name in class_lower or
                                    class_lower in arg_name or
                                    stripped in arg_name or
                                    arg_name in stripped):
                                    dependencies.add(class_name)

                    for sub_node in ast.walk(item):
                        if isinstance(sub_node, ast.Attribute):
                            if isinstance(sub_node.value, ast.Attribute):
                                if isinstance(sub_node.value.value, ast.Name):
                                    if sub_node.value.value.id == "self":
                                        method_called = sub_node.attr
                                        for other_cls in all_class_names:
                                            if other_cls == node.name:
                                                continue
                                            for other_node in ast.walk(tree):
                                                if isinstance(other_node, ast.ClassDef):
                                                    if other_node.name == other_cls:
                                                        other_methods = [
                                                            i.name for i in other_node.body
                                                            if isinstance(i, ast.FunctionDef)
                                                        ]
                                                        if method_called in other_methods:
                                                            dependencies.add(other_cls)

            facts["classes"].append({
                "name": node.name,
                "methods": methods,
                "dependencies": list(dependencies)
            })

        # Top level functions + call detection
        if isinstance(node, ast.FunctionDef):
            if node.name not in method_names and node.name != "__init__":
                facts["functions"].append(node.name)

                for sub_node in ast.walk(node):
                    if isinstance(sub_node, ast.Call):
                        if isinstance(sub_node.func, ast.Name):
                            called = sub_node.func.id
                            if called in all_function_names and called != node.name:
                                facts["calls"].append({
                                    "from": node.name,
                                    "to": called
                                })
                        elif isinstance(sub_node.func, ast.Attribute):
                            called = sub_node.func.attr
                            if called in all_function_names and called != node.name:
                                facts["calls"].append({
                                    "from": node.name,
                                    "to": called
                                })

        if isinstance(node, ast.Import):
            for alias in node.names:
                facts["imports"].append(alias.name)

        if isinstance(node, ast.ImportFrom):
            if node.module:
                facts["imports"].append(node.module)

    # Deduplicate calls
    seen = set()
    unique_calls = []
    for call in facts["calls"]:
        key = f"{call['from']}->{call['to']}"
        if key not in seen:
            seen.add(key)
            unique_calls.append(call)
    facts["calls"] = unique_calls

    return facts


def extract_with_ai(facts):
    """
    Builds nodes and edges directly from AST facts.
    Pure Python — zero AI, zero hallucination.
    """
    nodes = []
    edges = []
    id_counter = [1]

    def next_id():
        current = str(id_counter[0])
        id_counter[0] += 1
        return current

    if facts["classes"]:
        class_id_map = {}

        for cls in facts["classes"]:
            class_node_id = next_id()
            class_id_map[cls["name"]] = class_node_id
            nodes.append({
                "id": class_node_id,
                "label": cls["name"],
                "type": "class"
            })

        for cls in facts["classes"]:
            class_node_id = class_id_map[cls["name"]]

            for method in cls["methods"]:
                method_id = next_id()
                nodes.append({
                    "id": method_id,
                    "label": method,
                    "type": "method"
                })
                edges.append({
                    "from": class_node_id,
                    "to": method_id,
                    "label": "has method"
                })

            for dep in cls["dependencies"]:
                if dep in class_id_map:
                    edges.append({
                        "from": class_node_id,
                        "to": class_id_map[dep],
                        "label": "depends on"
                    })

    else:
        # Procedural code — use functions with call relationships
        func_id_map = {}

        for func in facts.get("functions", []):
            func_id = next_id()
            func_id_map[func] = func_id
            nodes.append({
                "id": func_id,
                "label": func,
                "type": "function"
            })

        # Add call edges
        for call in facts.get("calls", []):
            from_func = call["from"]
            to_func = call["to"]
            if from_func in func_id_map and to_func in func_id_map:
                edges.append({
                    "from": func_id_map[from_func],
                    "to": func_id_map[to_func],
                    "label": "calls"
                })

    return {"nodes": nodes, "edges": edges}


def _fallback_description(facts):
    """Build a structured description from facts when Ollama is unavailable."""
    lines = []
    classes = facts.get("classes", [])
    functions = facts.get("functions", [])

    if not classes and not functions:
        return "No analyzable structure found."

    # Overview
    if classes:
        names = [c["name"] for c in classes]
        lines.append("Overview:")
        lines.append(f"This codebase defines {len(classes)} class(es): {', '.join(names)}. ")
        if functions:
            lines.append(f"There are also {len(functions)} top-level function(s). ")
        lines.append("The structure is derived from the code; run Ollama (localhost:11434, model llama3.2) for an AI-generated summary.")
    else:
        lines.append("Overview:")
        lines.append(f"This codebase has {len(functions)} top-level function(s): {', '.join(functions[:10])}" + ("..." if len(functions) > 10 else "") + ". ")
        lines.append("Run Ollama for an AI-generated summary.")

    lines.append("")
    lines.append("Components:")

    for cls in classes:
        methods = cls.get("methods", [])[:5]
        deps = cls.get("dependencies", [])
        methods_str = ", ".join(methods) if methods else "none"
        deps_str = f"; depends on {', '.join(deps)}" if deps else ""
        lines.append(f"- {cls['name']}: methods ({methods_str}){deps_str}")

    for func in functions[:15]:
        lines.append(f"- function: {func}")

    if len(functions) > 15:
        lines.append(f"- ... and {len(functions) - 15} more functions")

    lines.append("")
    lines.append("Architecture Pattern:")
    if classes and not functions:
        lines.append("Object-oriented structure with classes and dependencies.")
    elif functions and not classes:
        lines.append("Procedural or functional structure with top-level functions and calls.")
    else:
        lines.append("Mixed structure with both classes and top-level functions.")

    return "\n".join(lines)


def generate_description(facts, diagram_data):
    """
    Uses Ollama to generate a plain English description
    of the codebase based on extracted facts.
    Falls back to a structured text description if Ollama is unavailable.
    """
    class_summary = []

    if facts.get("classes"):
        for cls in facts["classes"]:
            class_summary.append(
                f"- {cls['name']}: methods are {cls['methods']}, depends on {cls['dependencies']}"
            )
        subject = "classes"
    else:
        for func in facts.get("functions", []):
            class_summary.append(f"- function: {func}")
        subject = "functions"

    if not class_summary:
        return "No analyzable structure found."

    prompt = f"""
You are an expert software architect reviewing a codebase.
Based on these {subject}, write a clean plain English description.

Facts:
{chr(10).join(class_summary)}

Write your response in exactly this format:

Overview:
[2-3 sentences describing what this codebase does overall]

Components:
[For each {subject[:-1]}, one bullet point describing what it does]

Architecture Pattern:
[One sentence identifying the architecture pattern]

Keep it concise and professional. No markdown. No extra text.
"""

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3.2",
                "prompt": prompt,
                "stream": False
            },
            timeout=15
        )
        response.raise_for_status()
        return response.json()["response"].strip()
    except Exception as e:
        print(f"Warning: Ollama unavailable ({str(e)}). Using structured fallback description.")
        return _fallback_description(facts)


def parse_file(filepath):
    """
    Master function — give it a file path, get back nodes, edges and description.
    """
    print(f"Reading {filepath}...")
    code = read_file(filepath)

    print("Extracting structure with AST...")
    facts = extract_with_ast(code)
    print(f"  Found {len(facts['classes'])} classes, {len(facts['imports'])} imports")

    diagram_data = extract_with_ai(facts)
    print(f"  Got {len(diagram_data['nodes'])} nodes, {len(diagram_data['edges'])} edges")

    print("Generating description...")
    description = generate_description(facts, diagram_data)
    print(f"Description preview: {description[:100]}")

    diagram_data["description"] = description

    return diagram_data


if __name__ == "__main__":
    filepath = sys.argv[1] if len(sys.argv) > 1 else "test_code.py"
    result = parse_file(filepath)
    print()
    print("=== FINAL OUTPUT ===")
    print(json.dumps(result, indent=2))
