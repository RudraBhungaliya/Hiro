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


def extract_facts(code, all_class_names):
    """
    Extract classes, methods, and dependencies from one file.
    Uses global class names for cross-file dependency detection.
    """
    tree = ast.parse(code)
    facts = {"classes": [], "functions": []}

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

                    # Strategy 1 — constructor arg name matching
                    if item.name == "__init__":
                        for arg in item.args.args:
                            arg_name = arg.arg.lower()
                            if arg_name == "self":
                                continue
                            for class_name in all_class_names:
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

                    # Strategy 2 — self.x.method() call detection
                    for sub_node in ast.walk(item):
                        if isinstance(sub_node, ast.Attribute):
                            if isinstance(sub_node.value, ast.Attribute):
                                if isinstance(sub_node.value.value, ast.Name):
                                    if sub_node.value.value.id == "self":
                                        attr_name = sub_node.value.attr.lower()
                                        for class_name in all_class_names:
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

        if isinstance(node, ast.FunctionDef):
            if node.name not in method_names and node.name != "__init__":
                facts["functions"].append(node.name)

    return facts


def parse_folder(folder_path):
    """
    Two-pass folder parser.
    Pass 1 — build all nodes globally.
    Pass 2 — build all edges using global node map.
    """
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

    # ── PASS 1 — collect all class names globally ──────────────
    all_class_names = get_all_class_names(py_files)
    print(f"Global classes found: {all_class_names}")
    print()

    # ── PASS 2 — extract facts from each file ──────────────────
    all_facts = []
    for py_file in py_files:
        try:
            code = py_file.read_text()
            facts = extract_facts(code, all_class_names)
            all_facts.append(facts)
            for cls in facts["classes"]:
                print(f"  {cls['name']} → dependencies: {cls['dependencies']}")
        except Exception as e:
            print(f"  Skipping {py_file.name} — {e}")

    print()

    # ── PASS 3 — build nodes first, then edges ──────────────────
    all_nodes = []
    all_edges = []
    global_class_id_map = {}
    id_counter = 1

    # Create ALL class nodes first across all files
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

    # Now create method nodes and ALL edges
    for facts in all_facts:
        for cls in facts["classes"]:
            class_node_id = global_class_id_map[cls["name"]]

            # Method nodes
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

            # Dependency edges — now works across files
            for dep in cls["dependencies"]:
                if dep in global_class_id_map:
                    all_edges.append({
                        "from": class_node_id,
                        "to": global_class_id_map[dep],
                        "label": "depends on"
                    })

    print(f"Total: {len(all_nodes)} nodes, {len(all_edges)} edges")

    return {"nodes": all_nodes, "edges": all_edges}