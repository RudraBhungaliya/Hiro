"""
Java Extractor using Tree-sitter
Extracts classes, methods, annotations, and @Autowired dependencies from Java/Spring Boot code.
"""

from models.universe_parser import get_node_text


def extract_java(tree, code):
    """
    Extract classes, methods, interfaces, annotations, and dependency injections from Java code.
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
        """Extract annotations from a node's modifiers sibling."""
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

    def get_field_annotations(field_node):
        """Extract annotations directly on a field_declaration node."""
        annotations = []
        for child in field_node.children:
            if child.type == 'modifiers':
                for mod in child.children:
                    if mod.type in ['marker_annotation', 'annotation']:
                        ann_name_node = mod.child_by_field_name('name')
                        if ann_name_node:
                            ann = get_node_text(ann_name_node, code).lstrip('@')
                            annotations.append(ann)
        return annotations

    def extract_autowired_dependencies(body_node):
        """
        Walk a class body and collect the type names of every @Autowired field.
        These represent injected dependencies — the real architectural edges.
        """
        dependencies = []
        if not body_node:
            return dependencies

        for child in body_node.children:
            if child.type == 'field_declaration':
                field_anns = get_field_annotations(child)

                # @Autowired or @Inject — both mean dependency injection
                if any(a in field_anns for a in ['Autowired', 'Inject', 'Resource']):
                    # The type is the first type_identifier or generic_type child
                    for fc in child.children:
                        if fc.type in ['type_identifier', 'generic_type',
                                       'scoped_type_identifier']:
                            dep_type = get_node_text(fc, code)
                            # Strip generics like List<StudentService> → StudentService
                            if '<' in dep_type:
                                dep_type = dep_type.split('<')[1].rstrip('>')
                            if dep_type and dep_type not in dependencies:
                                dependencies.append(dep_type)
                            break  # one type per field

        return dependencies

    def extract_constructor_injections(body_node, class_name):
        """
        Detect constructor injection — parameters whose types match known Spring beans.
        Returns list of injected type names.
        """
        dependencies = []
        if not body_node:
            return dependencies

        for child in body_node.children:
            if child.type == 'constructor_declaration':
                cname_node = child.child_by_field_name('name')
                if cname_node and get_node_text(cname_node, code) == class_name:
                    params = child.child_by_field_name('parameters')
                    if params:
                        for param in params.children:
                            if param.type == 'formal_parameter':
                                type_node = param.child_by_field_name('type')
                                if type_node:
                                    dep_type = get_node_text(type_node, code)
                                    if '<' in dep_type:
                                        dep_type = dep_type.split('<')[1].rstrip('>')
                                    if dep_type and dep_type not in dependencies:
                                        dependencies.append(dep_type)

        return dependencies

    def walk(node):
        # Extract class declarations
        if node.type == 'class_declaration':
            class_name_node = node.child_by_field_name('name')
            if class_name_node:
                class_name = get_node_text(class_name_node, code)

                # Get class-level annotations
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

                # Extract @Autowired field injections (most common Spring pattern)
                autowired_deps = extract_autowired_dependencies(body)

                # Also check constructor injection
                constructor_deps = extract_constructor_injections(body, class_name)

                # Merge and deduplicate
                all_deps = list(dict.fromkeys(autowired_deps + constructor_deps))

                class_info = {
                    'name':         class_name,
                    'methods':      methods,
                    'annotations':  annotations,
                    'dependencies': all_deps,
                    'type':         'class'
                }

                # Detect Spring patterns from annotations
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

                # SpringBootApplication = entry point
                if 'SpringBootApplication' in annotations:
                    class_info['type'] = 'entry'

                # @Component is a generic Spring bean
                if 'Component' in annotations and class_info['type'] == 'class':
                    class_info['type'] = 'service'

                facts['classes'].append(class_info)

        # Extract interface declarations
        elif node.type == 'interface_declaration':
            interface_name_node = node.child_by_field_name('name')
            if interface_name_node:
                interface_name = get_node_text(interface_name_node, code)

                # Check if it extends JpaRepository / CrudRepository
                annotations = get_annotations(node)
                superclass  = ''
                for child in node.children:
                    if child.type == 'super_interfaces':
                        superclass = get_node_text(child, code)

                interface_info = {
                    'name':        interface_name,
                    'annotations': annotations,
                    'extends':     superclass,
                    'type':        'interface',
                }

                # JPA repositories declared as interfaces
                if any(r in superclass for r in [
                    'JpaRepository', 'CrudRepository',
                    'PagingAndSortingRepository', 'MongoRepository'
                ]):
                    facts['spring_patterns']['repositories'].append(interface_name)
                    interface_info['type'] = 'repository'

                # Treat as a class entry so the AI engine picks it up
                facts['classes'].append(interface_info)
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
