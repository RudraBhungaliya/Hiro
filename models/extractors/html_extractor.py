"""
HTML Extractor using Tree-sitter
"""

from models.universe_parser import get_node_text


def extract_html(tree, code):
    facts = {
        'structure': [],
        'scripts': [],
        'stylesheets': [],
        'forms': [],
        'links': [],
        'titles': [],
        'all_tags': []
    }

    root = tree.root_node

    def get_tag_name(element_node):
        for child in element_node.children:
            if child.type in ['start_tag', 'self_closing_tag']:
                for tag_child in child.children:
                    if tag_child.type == 'tag_name':
                        return get_node_text(tag_child, code)
        return None

    def get_attribute(element_node, attr_name):
        for child in element_node.children:
            if child.type in ['start_tag', 'self_closing_tag']:
                for attr_child in child.children:
                    if attr_child.type == 'attribute':
                        name_node = attr_child.child_by_field_name('name')
                        if name_node and get_node_text(name_node, code) == attr_name:
                            value_node = attr_child.child_by_field_name('value')
                            if value_node:
                                return get_node_text(value_node, code).strip('"\'')
        return None

    def walk(node):
        if node.type == 'element':
            tag_name = get_tag_name(node)

            if tag_name:
                # Track ALL tags so we always have something to show
                if tag_name not in facts['all_tags']:
                    facts['all_tags'].append(tag_name)

                # Semantic structural elements
                if tag_name in ['header', 'nav', 'main', 'section', 'article', 'aside', 'footer', 'div', 'body', 'html']:
                    if tag_name not in facts['structure']:
                        facts['structure'].append(tag_name)

                # Script tags
                if tag_name == 'script':
                    src = get_attribute(node, 'src')
                    if src:
                        facts['scripts'].append(src)
                    else:
                        # Inline script — still note it
                        if 'inline_script' not in facts['scripts']:
                            facts['scripts'].append('inline_script')

                # Stylesheets
                if tag_name == 'link':
                    rel = get_attribute(node, 'rel')
                    if rel == 'stylesheet':
                        href = get_attribute(node, 'href')
                        if href:
                            facts['stylesheets'].append(href)

                # Anchor links
                if tag_name == 'a':
                    href = get_attribute(node, 'href')
                    if href:
                        facts['links'].append(href)

                # Title
                if tag_name == 'title':
                    for child in node.children:
                        if child.type == 'text':
                            title_text = get_node_text(child, code).strip()
                            if title_text:
                                facts['titles'].append(title_text)

                # Forms
                if tag_name == 'form':
                    action = get_attribute(node, 'action') or ''
                    method = get_attribute(node, 'method') or 'GET'
                    facts['forms'].append({
                        'action': action,
                        'method': method
                    })

        for child in node.children:
            walk(child)

    walk(root)

    return facts