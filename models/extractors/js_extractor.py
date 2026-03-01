"""
JavaScript/React/Node.js Extractor using Tree-sitter
"""

from models.universe_parser import get_node_text


def extract_javascript(tree, code):
    facts = {
        'components': [],
        'functions':  [],
        'hooks':      [],
        'exports':    [],
        'imports':    [],
        'classes':    [],
        'requires':   [],
        'calls':      []
    }

    root = tree.root_node
    all_function_names = []

    def has_jsx_in_subtree(node):
        if 'jsx' in node.type:
            return True
        for child in node.children:
            if has_jsx_in_subtree(child):
                return True
        return False

    # First pass — collect all function names
    def collect_names(node):
        if node.type == 'function_declaration':
            name_node = node.child_by_field_name('name')
            if name_node:
                all_function_names.append(get_node_text(name_node, code))
        elif node.type in ['lexical_declaration', 'variable_declaration']:
            for child in node.children:
                if child.type == 'variable_declarator':
                    name_node  = child.child_by_field_name('name')
                    value_node = child.child_by_field_name('value')
                    if name_node and value_node and value_node.type == 'arrow_function':
                        all_function_names.append(get_node_text(name_node, code))
        for child in node.children:
            collect_names(child)

    collect_names(root)

    def walk(node, current_function=None):
        # Function declarations
        if node.type == 'function_declaration':
            name_node = node.child_by_field_name('name')
            if name_node:
                func_name = get_node_text(name_node, code)
                if func_name and func_name[0].isupper() and has_jsx_in_subtree(node):
                    facts['components'].append({'name': func_name, 'type': 'functional_component'})
                else:
                    if func_name and func_name not in facts['functions']:
                        facts['functions'].append(func_name)
                for child in node.children:
                    walk(child, func_name)
                return

        # Arrow functions / variable declarations
        elif node.type in ['lexical_declaration', 'variable_declaration']:
            for child in node.children:
                if child.type == 'variable_declarator':
                    name_node  = child.child_by_field_name('name')
                    value_node = child.child_by_field_name('value')
                    if name_node and value_node:
                        var_name = get_node_text(name_node, code)
                        if value_node.type == 'arrow_function':
                            if var_name and var_name[0].isupper() and has_jsx_in_subtree(value_node):
                                facts['components'].append({'name': var_name, 'type': 'functional_component'})
                            else:
                                if var_name and var_name not in facts['functions']:
                                    facts['functions'].append(var_name)
                            for sub in value_node.children:
                                walk(sub, var_name)
                            continue
                        elif value_node.type == 'call_expression':
                            func_node = value_node.child_by_field_name('function')
                            if func_node and get_node_text(func_node, code) == 'require':
                                args = value_node.child_by_field_name('arguments')
                                if args:
                                    for arg in args.children:
                                        if arg.type == 'string':
                                            req_path = get_node_text(arg, code).strip('"\'')
                                            facts['requires'].append(req_path)
                for subchild in child.children:
                    walk(subchild, current_function)
            return

        # Class declarations
        elif node.type == 'class_declaration':
            name_node = node.child_by_field_name('name')
            if name_node:
                class_name = get_node_text(name_node, code)
                methods = []
                body = node.child_by_field_name('body')
                if body:
                    for child in body.children:
                        if child.type == 'method_definition':
                            method_name_node = child.child_by_field_name('name')
                            if method_name_node:
                                method_name = get_node_text(method_name_node, code)
                                if method_name != 'constructor':
                                    methods.append(method_name)
                facts['classes'].append({'name': class_name, 'methods': methods})

        # Call expressions
        elif node.type == 'call_expression':
            func_node = node.child_by_field_name('function')
            if func_node:
                called_name = None
                if func_node.type == 'identifier':
                    called_name = get_node_text(func_node, code)
                elif func_node.type == 'member_expression':
                    prop = func_node.child_by_field_name('property')
                    if prop:
                        called_name = get_node_text(prop, code)

                if called_name:
                    if called_name.startswith('use') and len(called_name) > 3 and called_name[3].isupper():
                        if called_name not in facts['hooks']:
                            facts['hooks'].append(called_name)

                    if current_function and called_name in all_function_names and called_name != current_function:
                        call = {'from': current_function, 'to': called_name}
                        if call not in facts['calls']:
                            facts['calls'].append(call)

        # module.exports
        elif node.type == 'expression_statement':
            expr = node.children[0] if node.children else None
            if expr and expr.type == 'assignment_expression':
                left  = expr.child_by_field_name('left')
                right = expr.child_by_field_name('right')
                if left and get_node_text(left, code).startswith('module.exports'):
                    if right:
                        facts['exports'].append(get_node_text(right, code)[:50])

        # ES imports — capture both the module path AND named imports
        elif node.type == 'import_statement':
            source_node = node.child_by_field_name('source')
            if source_node:
                import_path = get_node_text(source_node, code).strip('"\'')
                facts['imports'].append(import_path)

                # Also treat local relative imports as require() equivalents
                # so the AI can infer cross-file edges
                if import_path.startswith('.'):
                    facts['requires'].append(import_path)

        for child in node.children:
            walk(child, current_function)

    walk(root)

    if facts['hooks']:
        facts['react_patterns'] = analyze_react_patterns(facts)

    return facts


def analyze_react_patterns(facts):
    patterns = []
    if 'useReducer' in facts['hooks']:
        patterns.append('reducer_pattern')
    elif 'useContext' in facts['hooks']:
        patterns.append('context_api')
    elif 'useState' in facts['hooks']:
        patterns.append('local_state')
    if 'useEffect' in facts['hooks']:
        patterns.append('side_effects')
    standard_hooks = ['useState', 'useEffect', 'useContext', 'useReducer',
                      'useMemo', 'useCallback', 'useRef']
    custom_hooks = [h for h in facts['hooks'] if h not in standard_hooks]
    if custom_hooks:
        patterns.append('custom_hooks')
    return patterns
