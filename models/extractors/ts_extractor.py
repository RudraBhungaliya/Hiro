"""
TypeScript Extractor using Tree-sitter
Extracts types, interfaces, components from TypeScript/TSX code.
"""

from models.universe_parser import get_node_text
from models.extractors.js_extractor import extract_javascript


def extract_typescript(tree, code):
    """
    Extract types, interfaces, components from TypeScript.
    
    Reuses JavaScript extractor and adds TypeScript-specific features:
    - Interfaces
    - Type aliases
    - Enums
    - Generic types
    """
    
    # Start with JavaScript extraction (TypeScript is superset of JS)
    facts = extract_javascript(tree, code)
    
    # Add TypeScript-specific
    facts['interfaces'] = []
    facts['types'] = []
    facts['enums'] = []
    
    root = tree.root_node
    
    def walk(node):
        # Extract interfaces
        if node.type == 'interface_declaration':
            name_node = node.child_by_field_name('name')
            if name_node:
                interface_name = get_node_text(name_node, code)
                facts['interfaces'].append(interface_name)
        
        # Extract type aliases
        elif node.type == 'type_alias_declaration':
            name_node = node.child_by_field_name('name')
            if name_node:
                type_name = get_node_text(name_node, code)
                facts['types'].append(type_name)
        
        # Extract enums
        elif node.type == 'enum_declaration':
            name_node = node.child_by_field_name('name')
            if name_node:
                enum_name = get_node_text(name_node, code)
                facts['enums'].append(enum_name)
        
        # Recurse
        for child in node.children:
            walk(child)
    
    walk(root)
    
    return facts