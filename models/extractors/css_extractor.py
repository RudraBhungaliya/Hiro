"""
CSS Extractor using Tree-sitter
"""

from models.universe_parser import get_node_text


def extract_css(tree, code):
    facts = {
        'classes': [],
        'ids': [],
        'media_queries': [],
        'animations': [],
        'selectors': [],
        'properties': []
    }

    root = tree.root_node

    def walk(node):
        # Class selectors
        if node.type == 'class_selector':
            for child in node.children:
                if child.type == 'class_name':
                    class_name = get_node_text(child, code)
                    if class_name not in facts['classes']:
                        facts['classes'].append(class_name)

        # ID selectors
        elif node.type == 'id_selector':
            for child in node.children:
                if child.type == 'id_name':
                    id_name = get_node_text(child, code)
                    if id_name not in facts['ids']:
                        facts['ids'].append(id_name)

        # Tag/element selectors — catch plain CSS like body, h1, p
        elif node.type == 'tag_name':
            tag = get_node_text(node, code)
            if tag and tag not in facts['selectors']:
                facts['selectors'].append(tag)

        # Rule sets — extract property names
        elif node.type == 'rule_set':
            for child in node.children:
                if child.type == 'block':
                    for block_child in child.children:
                        if block_child.type == 'declaration':
                            prop_node = block_child.child_by_field_name('property')
                            if prop_node:
                                prop = get_node_text(prop_node, code)
                                if prop and prop not in facts['properties']:
                                    facts['properties'].append(prop)

        # Media queries
        elif node.type == 'media_statement':
            media_text = get_node_text(node, code)
            if '{' in media_text:
                media_query = media_text.split('{')[0].strip()
                if media_query not in facts['media_queries']:
                    facts['media_queries'].append(media_query)

        # Keyframes
        elif node.type == 'keyframes_statement':
            name_node = node.child_by_field_name('name')
            if name_node:
                anim_name = get_node_text(name_node, code)
                facts['animations'].append(anim_name)

        for child in node.children:
            walk(child)

    walk(root)

    return facts