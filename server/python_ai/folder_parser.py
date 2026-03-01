import ast
from pathlib import Path


def get_all_class_names(py_files):
    """First pass — collect every class name across all files."""
    all_classes = []
    for py_file in py_files:
        try:
            code = py_file.read_text()
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    all_classes.append(node.name)
        except Exception:
            continue
    return all_classes


def detect_class_usage(py_files, all_class_names):
    """
    Detects which classes instantiate or use other classes.
    Strategy 1 — direct instantiation like Student()
    Strategy 2 — method parameter names hinting at class
    Returns list of from/to relationships.
    """
    relationships = []

    for py_file in py_files:
        try:
            code = py_file.read_text()
            tree = ast.parse(code)

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    current_class = node.name

                    for sub in ast.walk(node):

                        # Strategy 1 — direct instantiation like Student()
                        if isinstance(sub, ast.Call):
                            if isinstance(sub.func, ast.Name):
                                called_name = sub.func.id
                                if (called_name in all_class_names and
                                        called_name != current_class):
                                    relationships.append({
                                        "from": current_class,
                                        "to": called_name
                                    })
                            elif isinstance(sub.func, ast.Attribute):
                                if isinstance(sub.func.value, ast.Name):
                                    called_name = sub.func.value.id
                                    if (called_name in all_class_names and
                                            called_name != current_class):
                                        relationships.append({
                                            "from": current_class,
                                            "to": called_name
                                        })

                        # Strategy 2 — method parameter names hinting at class
                        if isinstance(sub, ast.FunctionDef):
                            for arg in sub.args.args:
                                arg_name = arg.arg.lower()
                                if arg_name == "self":
                                    continue
                                for class_name in all_class_names:
                                    if class_name == current_class:
                                        continue
                                    class_lower = class_name.lower()
                                    # Only match if class name is at least 6 chars
                                    # to avoid false positives like "car"
                                    stripped_class = class_lower.rstrip("s")
                                    if (len(class_lower) >= 6 and
                                        (stripped_class == arg_name or
                                         stripped_class in arg_name or
                                         arg_name == class_lower)):
                                        relationships.append({
                                            "from": current_class,
                                            "to": class_name
                                        })

        except Exception:
            continue

    # Deduplicate
    seen = set()
    unique = []
    for r in relationships:
        key = f"{r['from']}->{r['to']}"
        if key not in seen:
            seen.add(key)
            unique.append(r)

    return unique


def extract_facts(code, all_function_names_global):
    """
    Extract functions and calls from one file.
    Uses global function names for cross-file call detection.
    """
    tree = ast.parse(code)
    facts = {"classes": [], "functions": [], "calls": [], "imports": []}

    method_names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    method_names.add(item.name)

    # Get functions defined in this file
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            if node.name not in method_names and node.name != "__init__":
                facts["functions"].append(node.name)

    # Detect calls inside every function body
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            if node.name not in method_names and node.name != "__init__":
                for sub_node in ast.walk(node):
                    if isinstance(sub_node, ast.Call):
                        if isinstance(sub_node.func, ast.Name):
                            called = sub_node.func.id
                            if called in all_function_names_global and called != node.name:
                                facts["calls"].append({
                                    "from": node.name,
                                    "to": called
                                })

    # Detect calls in if __name__ == "__main__" block
    for node in ast.walk(tree):
        if isinstance(node, ast.If):
            test = node.test
            is_main_block = False
            if isinstance(test, ast.Compare):
                if isinstance(test.left, ast.Name) and test.left.id == "__name__":
                    is_main_block = True

            if is_main_block:
                if "main" not in facts["functions"]:
                    facts["functions"].append("main")
                for sub_node in ast.walk(node):
                    if isinstance(sub_node, ast.Call):
                        if isinstance(sub_node.func, ast.Name):
                            called = sub_node.func.id
                            if called in all_function_names_global:
                                facts["calls"].append({
                                    "from": "main",
                                    "to": called
                                })

    # Handle classes
    all_class_names_local = [
        node.name for node in ast.walk(tree)
        if isinstance(node, ast.ClassDef)
    ]

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
                            for class_name in all_class_names_local:
                                if class_name == node.name:
                                    continue
                                class_lower = class_name.lower()
                                stripped = class_lower
                                for suffix in ["service", "manager", "repository", "controller"]:
                                    stripped = stripped.replace(suffix, "").strip()
                                if (arg_name in class_lower or
                                    class_lower in arg_name or
                                    stripped in arg_name or
                                    arg_name in stripped or
                                    (len(arg_name) <= 4 and stripped.startswith(arg_name)) or
                                    (len(arg_name) <= 4 and arg_name in stripped)):
                                    dependencies.add(class_name)

                    for sub_node in ast.walk(item):
                        if isinstance(sub_node, ast.Attribute):
                            if isinstance(sub_node.value, ast.Attribute):
                                if isinstance(sub_node.value.value, ast.Name):
                                    if sub_node.value.value.id == "self":
                                        attr_name = sub_node.value.attr.lower()
                                        for class_name in all_class_names_local:
                                            if class_name == node.name:
                                                continue
                                            class_lower = class_name.lower()
                                            stripped = class_lower
                                            for suffix in ["service", "manager", "repository"]:
                                                stripped = stripped.replace(suffix, "").strip()
                                            if (attr_name in class_lower or
                                                stripped in attr_name or
                                                attr_name in stripped or
                                                (len(attr_name) <= 4 and stripped.startswith(attr_name))):
                                                dependencies.add(class_name)

            facts["classes"].append({
                "name": node.name,
                "methods": methods,
                "dependencies": list(dependencies)
            })

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


def parse_folder(folder_path):
    """
    Multi-pass folder parser.
    Pass 1  — collect all class names globally.
    Pass 1b — collect all function names globally.
    Pass 1c — detect cross-class usage relationships.
    Pass 2  — extract facts from each file.
    Pass 3  — build all nodes and edges.
    Pass 4  — generate description.
    """
    from parser import generate_description

    folder = Path(folder_path)

    if not folder.exists():
        raise FileNotFoundError(f"Folder not found: {folder_path}")

    py_files = list(folder.rglob("*.py"))
    py_files = [
        f for f in py_files
        if "__pycache__" not in str(f)
        and "venv" not in str(f)
        and f.name != "__init__.py"
    ]

    if not py_files:
        raise ValueError(f"No .py files found in {folder_path}")

    print(f"Found {len(py_files)} Python files:")
    for f in py_files:
        print(f"  → {f.name}")
    print()

    # Pass 1 — collect all class names globally
    all_class_names = get_all_class_names(py_files)
    print(f"Global classes found: {all_class_names}")

    # Pass 1b — collect all function names globally
    all_function_names_global = []
    for py_file in py_files:
        try:
            code = py_file.read_text()
            tree = ast.parse(code)
            method_names = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            method_names.add(item.name)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if node.name not in method_names and node.name != "__init__":
                        all_function_names_global.append(node.name)
        except Exception:
            continue

    all_function_names_global.append("main")
    print(f"Global functions found: {all_function_names_global}")

    # Pass 1c — detect cross-class usage
    class_relationships = detect_class_usage(py_files, all_class_names)
    print(f"Class relationships found: {class_relationships}")
    print()

    # Pass 2 — extract facts from each file
    all_facts = []
    for py_file in py_files:
        try:
            code = py_file.read_text()
            facts = extract_facts(code, all_function_names_global)
            all_facts.append(facts)
            print(f"  {py_file.name} → functions: {facts['functions']}, calls: {facts['calls']}")
        except Exception as e:
            print(f"  Skipping {py_file.name} — {e}")

    print()

    # Pass 3 — build all nodes first then edges
    all_nodes = []
    all_edges = []
    global_class_id_map = {}
    id_counter = 1

    # Create all class nodes first
    for facts in all_facts:
        for cls in facts["classes"]:
            node_id = str(id_counter)
            id_counter += 1
            global_class_id_map[cls["name"]] = node_id
            all_nodes.append({
                "id": node_id,
                "label": cls["name"],
                "type": "class"
            })

    # Create method nodes and class edges
    for facts in all_facts:
        for cls in facts["classes"]:
            class_node_id = global_class_id_map[cls["name"]]

            for method in cls["methods"]:
                method_id = str(id_counter)
                id_counter += 1
                all_nodes.append({
                    "id": method_id,
                    "label": method,
                    "type": "method"
                })
                all_edges.append({
                    "from": class_node_id,
                    "to": method_id,
                    "label": "has method"
                })

            for dep in cls["dependencies"]:
                if dep in global_class_id_map:
                    all_edges.append({
                        "from": class_node_id,
                        "to": global_class_id_map[dep],
                        "label": "depends on"
                    })

    # Add cross-class usage edges
    for rel in class_relationships:
        from_cls = rel["from"]
        to_cls = rel["to"]
        if from_cls in global_class_id_map and to_cls in global_class_id_map:
            all_edges.append({
                "from": global_class_id_map[from_cls],
                "to": global_class_id_map[to_cls],
                "label": "uses"
            })

    # Handle procedural files with no classes
    all_functions = []
    all_calls = []
    for facts in all_facts:
        all_functions.extend(facts.get("functions", []))
        all_calls.extend(facts.get("calls", []))

    if not all_nodes and all_functions:
        print(f"  No classes found — building function graph")
        func_id_map = {}

        seen_funcs = set()
        unique_functions = []
        for func in all_functions:
            if func not in seen_funcs:
                seen_funcs.add(func)
                unique_functions.append(func)

        for func in unique_functions:
            func_id = str(id_counter)
            id_counter += 1
            func_id_map[func] = func_id
            all_nodes.append({
                "id": func_id,
                "label": func,
                "type": "function"
            })

        seen = set()
        for call in all_calls:
            key = f"{call['from']}->{call['to']}"
            if (key not in seen and
                call["from"] in func_id_map and
                call["to"] in func_id_map):
                seen.add(key)
                all_edges.append({
                    "from": func_id_map[call["from"]],
                    "to": func_id_map[call["to"]],
                    "label": "calls"
                })

    print(f"Total: {len(all_nodes)} nodes, {len(all_edges)} edges")

    # Pass 4 — generate description
    print("Generating description...")
    combined_facts = {"classes": [], "functions": []}
    for facts in all_facts:
        combined_facts["classes"].extend(facts["classes"])
        combined_facts["functions"].extend(facts.get("functions", []))

    if combined_facts["classes"] or combined_facts["functions"]:
        description = generate_description(
            combined_facts,
            {"nodes": all_nodes, "edges": all_edges}
        )
        print(f"Description preview: {description[:100]}")
    else:
        description = "No analyzable structure found in this folder."
        print("Nothing to describe.")

    return {
        "nodes": all_nodes,
        "edges": all_edges,
        "description": description
    }
