"""
Python Extractor using Tree-sitter
Extracts classes, methods, functions, imports, and call relationships from Python code.
"""

from models.universe_parser import get_node_text


def extract_python(tree, code):
    """
    Extract classes, methods, functions, imports, and inter-function calls from Python code.

    Args:
        tree: Tree-sitter parse tree
        code: Source code as bytes

    Returns:
        dict with classes, functions, imports, calls
    """

    facts = {
        'classes':      [],
        'functions':    [],
        'imports':      [],
        'requires':     [],   # mirrors JS convention so AI engine treats them uniformly
        'calls':        [],
        'dependencies': []
    }

    root = tree.root_node

    # ── First pass: collect all top-level function names ──────
    all_top_level_functions = []
    method_names = set()

    def collect_method_names(node):
        if node.type == 'class_definition':
            body = node.child_by_field_name('body')
            if body:
                for child in body.children:
                    if child.type == 'function_definition':
                        name_node = child.child_by_field_name('name')
                        if name_node:
                            method_names.add(get_node_text(name_node, code))
        for child in node.children:
            collect_method_names(child)

    collect_method_names(root)

    for node in root.children:
        if node.type == 'function_definition':
            name_node = node.child_by_field_name('name')
            if name_node:
                fname = get_node_text(name_node, code)
                if fname != '__init__' and fname not in method_names:
                    all_top_level_functions.append(fname)

    # ── Main walk ─────────────────────────────────────────────
    def walk(node):
        # Class definitions
        if node.type == 'class_definition':
            class_name_node = node.child_by_field_name('name')
            if class_name_node:
                class_name = get_node_text(class_name_node, code)

                methods      = []
                dependencies = []

                body = node.child_by_field_name('body')
                if body:
                    for child in body.children:
                        if child.type == 'function_definition':
                            method_name_node = child.child_by_field_name('name')
                            if method_name_node:
                                method_name = get_node_text(method_name_node, code)
                                if method_name != '__init__':
                                    methods.append(method_name)

                            # Detect injected dependencies via __init__ parameters
                            if method_name_node and get_node_text(method_name_node, code) == '__init__':
                                params = child.child_by_field_name('parameters')
                                if params:
                                    for param in params.children:
                                        if param.type in ['identifier', 'typed_parameter']:
                                            param_name = get_node_text(param, code).split(':')[0].strip()
                                            if param_name in ('self', 'cls', '*args', '**kwargs'):
                                                continue
                                            dependencies.append(param_name)

                facts['classes'].append({
                    'name':         class_name,
                    'methods':      methods,
                    'dependencies': dependencies,
                })

        # Top-level function definitions
        elif node.type == 'function_definition':
            if node.parent and node.parent.type == 'module':
                func_name_node = node.child_by_field_name('name')
                if func_name_node:
                    func_name = get_node_text(func_name_node, code)
                    if func_name != '__init__' and func_name not in method_names:
                        facts['functions'].append(func_name)

                        # Detect calls to other top-level functions
                        def find_calls(n, current_fn):
                            if n.type == 'call':
                                fn_node = n.child_by_field_name('function')
                                if fn_node:
                                    called = get_node_text(fn_node, code)
                                    # Strip attribute access e.g. self.foo → foo
                                    if '.' in called:
                                        called = called.split('.')[-1]
                                    if (called in all_top_level_functions
                                            and called != current_fn):
                                        call_entry = {'from': current_fn, 'to': called}
                                        if call_entry not in facts['calls']:
                                            facts['calls'].append(call_entry)
                            for child in n.children:
                                find_calls(child, current_fn)

                        find_calls(node, func_name)

        # import x
        elif node.type == 'import_statement':
            for child in node.children:
                if child.type == 'dotted_name':
                    import_name = get_node_text(child, code)
                    facts['imports'].append(import_name)

        # from x import y
        elif node.type == 'import_from_statement':
            module_name_node = node.child_by_field_name('module_name')
            if module_name_node:
                module_name = get_node_text(module_name_node, code)
                facts['imports'].append(module_name)

                # Relative imports (from .models import ...) become requires
                # so the AI can draw cross-file edges
                if module_name.startswith('.'):
                    facts['requires'].append(module_name)

        # Recurse
        for child in node.children:
            walk(child)

    walk(root)

    return facts
