"""
Python Extractor using Tree-sitter
Extracts classes, methods, functions, and dependencies from Python code.
"""

from models.universe_parser import get_node_text


def extract_python(tree, code):
    """
    Extract classes, methods, functions from Python code.
    
    Args:
        tree: Tree-sitter parse tree
        code: Source code as bytes
    
    Returns:
        dict with classes, functions, dependencies
    """
    
    facts = {
        'classes': [],
        'functions': [],
        'imports': [],
        'dependencies': []
    }
    
    root = tree.root_node
    
    # Walk through all nodes
    def walk(node):
        # Extract class definitions
        if node.type == 'class_definition':
            class_name_node = node.child_by_field_name('name')
            if class_name_node:
                class_name = get_node_text(class_name_node, code)
                
                # Extract methods inside this class
                methods = []
                body = node.child_by_field_name('body')
                if body:
                    for child in body.children:
                        if child.type == 'function_definition':
                            method_name_node = child.child_by_field_name('name')
                            if method_name_node:
                                method_name = get_node_text(method_name_node, code)
                                if method_name != '__init__':
                                    methods.append(method_name)
                
                facts['classes'].append({
                    'name': class_name,
                    'methods': methods,
                    'dependencies': []
                })
        
        # Extract top-level function definitions
        elif node.type == 'function_definition':
            # Check if it's top-level (parent is module)
            if node.parent and node.parent.type == 'module':
                func_name_node = node.child_by_field_name('name')
                if func_name_node:
                    func_name = get_node_text(func_name_node, code)
                    facts['functions'].append(func_name)
        
        # Extract imports
        elif node.type == 'import_statement':
            for child in node.children:
                if child.type == 'dotted_name':
                    import_name = get_node_text(child, code)
                    facts['imports'].append(import_name)
        
        elif node.type == 'import_from_statement':
            module_name = node.child_by_field_name('module_name')
            if module_name:
                facts['imports'].append(get_node_text(module_name, code))
        
        # Recurse to children
        for child in node.children:
            walk(child)
    
    walk(root)
    
    return facts