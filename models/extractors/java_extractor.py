"""
Java Extractor using Tree-sitter
Extracts classes, methods, annotations from Java/Spring Boot code.
"""

from models.universe_parser import get_node_text


def extract_java(tree, code):
    """
    Extract classes, methods, interfaces, annotations from Java code.
    """
    
    facts = {
        'classes': [],
        'interfaces': [],
        'imports': [],
        'spring_patterns': {
            'controllers': [],
            'services': [],
            'repositories': [],
            'entities': []
        }
    }
    
    root = tree.root_node
    
    def get_annotations(node):
        """Extract annotations from modifiers."""
        annotations = []
        parent = node.parent
        
        if parent:
            for sibling in parent.children:
                if sibling.type == 'modifiers':
                    for child in sibling.children:
                        if child.type in ['marker_annotation', 'annotation']:
                            ann_name_node = child.child_by_field_name('name')
                            if ann_name_node:
                                ann_name = get_node_text(ann_name_node, code)
                                ann_name = ann_name.lstrip('@')
                                annotations.append(ann_name)
        
        return annotations
    
    def walk(node):
        # Extract class declarations
        if node.type == 'class_declaration':
            class_name_node = node.child_by_field_name('name')
            if class_name_node:
                class_name = get_node_text(class_name_node, code)
                
                # Get annotations
                annotations = get_annotations(node)
                
                # Extract methods
                methods = []
                body = node.child_by_field_name('body')
                if body:
                    for child in body.children:
                        if child.type == 'method_declaration':
                            method_name_node = child.child_by_field_name('name')
                            if method_name_node:
                                methods.append(get_node_text(method_name_node, code))
                
                class_info = {
                    'name': class_name,
                    'methods': methods,
                    'annotations': annotations,
                    'type': 'class'
                }
                
                # Detect Spring patterns
                if any(ann in annotations for ann in ['RestController', 'Controller']):
                    facts['spring_patterns']['controllers'].append(class_name)
                    class_info['type'] = 'controller'
                
                if 'Service' in annotations:
                    facts['spring_patterns']['services'].append(class_name)
                    class_info['type'] = 'service'
                
                if 'Repository' in annotations:
                    facts['spring_patterns']['repositories'].append(class_name)
                    class_info['type'] = 'repository'
                
                if 'Entity' in annotations:
                    facts['spring_patterns']['entities'].append(class_name)
                    class_info['type'] = 'entity'
                
                facts['classes'].append(class_info)
        
        # Extract interface declarations
        elif node.type == 'interface_declaration':
            interface_name_node = node.child_by_field_name('name')
            if interface_name_node:
                interface_name = get_node_text(interface_name_node, code)
                facts['interfaces'].append(interface_name)
        
        # Extract imports
        elif node.type == 'import_declaration':
            for child in node.children:
                if child.type == 'scoped_identifier':
                    import_name = get_node_text(child, code)
                    facts['imports'].append(import_name)
        
        # Recurse
        for child in node.children:
            walk(child)
    
    walk(root)
    
    return facts