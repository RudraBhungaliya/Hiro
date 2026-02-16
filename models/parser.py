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
    Use Python's built-in AST to extract facts directly from code.
    Returns classes, their methods, dependencies, and imports.
    """
    tree = ast.parse(code)
    facts = {
        "classes": [],
        "imports": [],
        "functions": []
    }

    all_class_names = [
        node.name for node in ast.walk(tree)
        if isinstance(node, ast.ClassDef)
    ]

    # Track method names to exclude from top level functions
    method_names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    method_names.add(item.name)

    for node in ast.walk(tree):

        if isinstance(node, ast.ClassDef):
            methods = []
            dependencies = set()

            for item in node.body:
                if isinstance(item, ast.FunctionDef):

                    if item.name != "__init__":
                        methods.append(item.name)

                    # Strategy 1 — match constructor arg names to class names
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

                    # Strategy 2 — detect self.x.method() calls
                    # If self.db.query() is called, find what class has query()
                    for sub_node in ast.walk(item):
                        if isinstance(sub_node, ast.Attribute):
                            if isinstance(sub_node.value, ast.Attribute):
                                if isinstance(sub_node.value.value, ast.Name):
                                    if sub_node.value.value.id == "self":
                                        method_called = sub_node.attr
                                        for other_cls in all_class_names:
                                            if other_cls == node.name:
                                                continue
                                            # Check if that method belongs to another class
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

        # Top level functions only
        if isinstance(node, ast.FunctionDef):
            if node.name not in method_names and node.name != "__init__":
                facts["functions"].append(node.name)

        if isinstance(node, ast.Import):
            for alias in node.names:
                facts["imports"].append(alias.name)

        if isinstance(node, ast.ImportFrom):
            if node.module:
                facts["imports"].append(node.module)

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

        # First pass — create all class nodes
        for cls in facts["classes"]:
            class_node_id = next_id()
            class_id_map[cls["name"]] = class_node_id
            nodes.append({
                "id": class_node_id,
                "label": cls["name"],
                "type": "class"
            })

        # Second pass — create method nodes and dependency edges
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
        for func in facts.get("functions", []):
            func_id = next_id()
            nodes.append({
                "id": func_id,
                "label": func,
                "type": "function"
            })

    return {"nodes": nodes, "edges": edges}

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

    diagram_data["description"] = description

    return diagram_data

def generate_description(facts, diagram_data):
    """
    Uses Ollama to generate a plain English description
    of the codebase based on extracted facts.
    """
    class_summary = []
    for cls in facts["classes"]:
        class_summary.append(
            f"- {cls['name']}: methods are {cls['methods']}, depends on {cls['dependencies']}"
        )

    prompt = f"""
You are an expert software architect reviewing a codebase.
Based on these facts, write a clean plain English description.

Facts:
{chr(10).join(class_summary)}

Write your response in exactly this format:

Overview:
[2-3 sentences describing what this codebase does overall]

Components:
[For each class, one bullet point: ClassName — what it does and who it depends on]

Architecture Pattern:
[One sentence identifying the architecture pattern]

Keep it concise and professional. No markdown. No extra text.
"""

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3.2",
            "prompt": prompt,
            "stream": False
        }
    )

    return response.json()["response"].strip()


if __name__ == "__main__":
    filepath = sys.argv[1] if len(sys.argv) > 1 else "test_code.py"
    result = parse_file(filepath)
    print()
    print("=== FINAL OUTPUT ===")
    print(json.dumps(result, indent=2))