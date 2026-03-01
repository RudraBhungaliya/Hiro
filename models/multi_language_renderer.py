"""
Multi-Language Renderer - Backend Architecture Focus
"""

from pathlib import Path

LANGUAGE_STYLES = {
    'python':     {'icon': '🐍'},
    'java':       {'icon': '☕'},
    'javascript': {'icon': '⚡'},
    'typescript': {'icon': '📘'},
    'tsx':        {'icon': '⚛️'},
}

MAX_FILES_PER_LANGUAGE = 60
MAX_METHODS_PER_CLASS  = 6
MAX_FUNCTIONS_PER_FILE = 6


# ── FILE ROLE DETECTION ───────────────────────────────────────────────

def detect_file_role(filename, facts):
    name = filename.lower().replace('.java', '').replace('.js', '') \
                           .replace('.ts', '').replace('.py', '')
    funcs      = ' '.join(facts.get('functions', [])).lower()
    classes    = [c for c in facts.get('classes', []) if isinstance(c, dict)]
    class_names = ' '.join(c['name'] for c in classes).lower()
    combined   = name + ' ' + funcs + ' ' + class_names

    # Java Spring — use annotation-based type first
    if classes:
        types_present = [c.get('type', 'class') for c in classes]
        if 'controller' in types_present:
            return 'controller', 'Controller'
        if 'service' in types_present:
            return 'service', 'Service'
        if 'repository' in types_present:
            return 'repository', 'Repository'
        if 'entity' in types_present:
            return 'entity', 'Entity / Data Model'

    # Name-based detection
    if any(w in combined for w in ['controller']):
        return 'controller', 'Controller'
    if any(w in combined for w in ['service', 'manager']):
        return 'service', 'Service'
    if any(w in combined for w in ['repository', 'repo', 'dao']):
        return 'repository', 'Repository'
    if any(w in combined for w in ['entity', 'model', 'schema']):
        return 'entity', 'Entity / Data Model'
    if any(w in combined for w in ['validator', 'validation']):
        return 'validator', 'Validator'
    if any(w in combined for w in ['formatter', 'converter', 'serializer']):
        return 'formatter', 'Formatter'
    if any(w in combined for w in ['config', 'configuration', 'setup']):
        return 'config', 'Configuration'
    if any(w in combined for w in ['middleware', 'guard', 'interceptor', 'filter']):
        return 'middleware', 'Middleware'
    if any(w in combined for w in ['db', 'database', 'connection', 'pool', 'mongo',
                                    'mysql', 'postgres', 'sequelize', 'mongoose']):
        return 'database', 'Database'
    if any(w in combined for w in ['email', 'mail', 'smtp', 'notification']):
        return 'service', 'Email Service'
    if any(w in combined for w in ['auth', 'login', 'token', 'jwt', 'passport', 'session']):
        return 'middleware', 'Auth'
    if any(w in combined for w in ['util', 'helper', 'common', 'shared']):
        return 'utility', 'Utility'
    if any(w in combined for w in ['route', 'router', 'routing']):
        return 'router', 'Router'
    if any(w in combined for w in ['app', 'server', 'main', 'index', 'application']):
        return 'entry', 'Entry Point'

    return 'module', 'Module'


def role_shape(role, label):
    """Returns Mermaid node shape based on role."""
    shapes = {
        'entry':      f'["{label}"]',
        'router':     f'["{label}"]',
        'controller': f'["{label}"]',
        'service':    f'("{label}")',
        'model':      f'[/"{label}"/]',
        'repository': f'[/"{label}"/]',
        'database':   f'[("{label}")]',
        'middleware': f'{{"{label}"}}',
        'utility':    f'("{label}")',
        'module':     f'["{label}"]',
    }
    return shapes.get(role, f'["{label}"]')


def has_renderable_content(facts):
    if not isinstance(facts, dict):
        return False
    return any([
        facts.get('classes'),
        facts.get('components'),
        facts.get('functions'),
        facts.get('spring_patterns', {}).get('controllers'),
        facts.get('spring_patterns', {}).get('services'),
        facts.get('spring_patterns', {}).get('repositories'),
    ])


# ── AI DIAGRAM RENDERER ───────────────────────────────────────────────

def render_ai_diagram(result, output_path="diagram.mmd"):
    """
    Renders the AI-generated architecture result as a production-quality Mermaid diagram.
    Uses role-based shapes, colour styles, and semantic edge labels from the LLM.
    """
    diagram = result.get("diagram", {})
    nodes   = diagram.get("nodes", [])
    edges   = diagram.get("edges", [])
    desc    = result.get("description", {})

    # ── Shape map by role ─────────────────────────────────────
    ROLE_SHAPES = {
        "client":     lambda l: f'(["{l}"])',
        "entry":      lambda l: f'["{l}"]',
        "middleware": lambda l: f'{{"{l}"}}',
        "router":     lambda l: f'["{l}"]',
        "controller": lambda l: f'["{l}"]',
        "service":    lambda l: f'("{l}")',
        "repository": lambda l: f'[/"{l}"/]',
        "entity":     lambda l: f'[("{l}")]',
        "database":   lambda l: f'[("{l}")]',
        "utility":    lambda l: f'("{l}")',
        "external":   lambda l: f'(("{l}"))',
        "module":     lambda l: f'["{l}"]',
    }

    # ── Colour styles by role ─────────────────────────────────
    ROLE_STYLES = {
        "client":     "fill:#16213e,color:#90caf9,stroke:#42a5f5,stroke-width:2px",
        "entry":      "fill:#1a237e,color:#fff,stroke:#5c6bc0,stroke-width:2px",
        "middleware": "fill:#4a148c,color:#ce93d8,stroke:#ab47bc,stroke-width:2px",
        "router":     "fill:#01579b,color:#81d4fa,stroke:#29b6f6,stroke-width:2px",
        "controller": "fill:#0d47a1,color:#fff,stroke:#1565c0,stroke-width:2px",
        "service":    "fill:#4527a0,color:#fff,stroke:#7e57c2,stroke-width:2px",
        "repository": "fill:#1b5e20,color:#a5d6a7,stroke:#43a047,stroke-width:2px",
        "entity":     "fill:#1a3c2c,color:#80cbc4,stroke:#26a69a,stroke-width:2px",
        "database":   "fill:#0d1f12,color:#69f0ae,stroke:#00e676,stroke-width:3px",
        "utility":    "fill:#263238,color:#cfd8dc,stroke:#78909c,stroke-width:1px",
        "external":   "fill:#3e0000,color:#ff8a80,stroke:#ff1744,stroke-width:2px",
        "module":     "fill:#212121,color:#eeeeee,stroke:#757575,stroke-width:1px",
    }

    # ── Render order — top to bottom visually ─────────────────
    ROLE_ORDER = [
        "client", "entry", "middleware", "router",
        "controller", "service", "repository",
        "entity", "database", "external", "utility", "module",
    ]

    lines = ["graph TD", ""]

    # Group nodes by role
    role_groups = {}
    for node in nodes:
        role = node.get("role", "module")
        role_groups.setdefault(role, []).append(node)

    emitted_ids = set()

    for role in ROLE_ORDER:
        group = role_groups.get(role, [])
        if not group:
            continue

        lines.append(f"    %% {role.upper()} LAYER")
        for node in group:
            nid      = node["id"]
            label    = node["label"]
            shape_fn = ROLE_SHAPES.get(role, lambda l: f'["{l}"]')
            lines.append(f"    {nid}{shape_fn(label)}")
            emitted_ids.add(nid)
        lines.append("")

    # Emit any leftover nodes not matched by role order
    leftover = [n for n in nodes if n["id"] not in emitted_ids]
    if leftover:
        lines.append("    %% OTHER")
        for node in leftover:
            nid      = node["id"]
            label    = node["label"]
            role     = node.get("role", "module")
            shape_fn = ROLE_SHAPES.get(role, lambda l: f'["{l}"]')
            lines.append(f"    {nid}{shape_fn(label)}")
            emitted_ids.add(nid)
        lines.append("")

    # ── Edges ─────────────────────────────────────────────────
    lines.append("    %% EDGES")
    seen_edges = set()

    for edge in edges:
        frm   = edge.get("from", "")
        to    = edge.get("to", "")
        label = edge.get("label", "")

        # Skip edges referencing nodes that don't exist
        if frm not in emitted_ids or to not in emitted_ids:
            continue

        # Deduplicate
        edge_key = f"{frm}->{to}"
        if edge_key in seen_edges:
            continue
        seen_edges.add(edge_key)

        # Truncate very long labels so Mermaid doesn't break
        if len(label) > 48:
            label = label[:45] + "..."

        # Escape pipe characters in labels (breaks Mermaid syntax)
        label = label.replace("|", "/")

        lines.append(f'    {frm} -->|"{label}"| {to}')

    lines.append("")

    # ── Style declarations ────────────────────────────────────
    lines.append("    %% STYLES")
    node_by_id = {n["id"]: n for n in nodes}
    for nid in emitted_ids:
        node  = node_by_id.get(nid)
        if not node:
            continue
        role  = node.get("role", "module")
        style = ROLE_STYLES.get(role, ROLE_STYLES["module"])
        lines.append(f"    style {nid} {style}")

    mermaid_code = "\n".join(lines)

    # ── Build text description ────────────────────────────────
    overview    = desc.get("overview", "")
    components  = desc.get("components", [])
    arch        = desc.get("architecture_pattern", "")
    proj_name   = result.get("project_name", "Architecture Diagram")

    desc_lines = []
    desc_lines.append(f"PROJECT: {proj_name}")
    desc_lines.append("=" * 60)

    if overview:
        desc_lines.append("")
        desc_lines.append("OVERVIEW")
        desc_lines.append("-" * 40)
        desc_lines.append(overview)

    if components:
        desc_lines.append("")
        desc_lines.append("COMPONENTS")
        desc_lines.append("-" * 40)
        for comp in components:
            desc_lines.append(f"  • {comp.get('name', '')}  [{comp.get('role', '')}]")
            desc_lines.append(f"    {comp.get('what_it_does', '')}")
            desc_lines.append("")

    if arch:
        desc_lines.append("ARCHITECTURE PATTERN")
        desc_lines.append("-" * 40)
        desc_lines.append(arch)

    description = "\n".join(desc_lines)

    # ── Print & save ──────────────────────────────────────────
    print("=== MERMAID CODE ===")
    print(mermaid_code)
    print()
    print("=== DESCRIPTION ===")
    print(description)
    print()

    Path(output_path).write_text(mermaid_code + "\n\n---\n" + description,
                                  encoding="utf-8")
    print(f"✓ Diagram saved → {output_path}")

    return mermaid_code, description


# ── LEGACY DIAGRAM BUILDER (used by --file mode) ──────────────────────

def build_mermaid_multi_language(all_facts):
    lines = ["graph TD"]
    lines.append("")
    edges = []

    id_counter    = 1
    file_node_map = {}
    all_calls     = []

    for language, facts_list in all_facts.items():
        if not facts_list:
            continue

        facts_list = facts_list[:MAX_FILES_PER_LANGUAGE]
        style = LANGUAGE_STYLES.get(language, {'icon': '📄'})

        lines.append(f"    %% {language.upper()}")

        for facts in facts_list:
            if not isinstance(facts, dict):
                continue
            if not has_renderable_content(facts):
                continue

            filename = facts.get('filename', 'unknown')
            role, role_label = detect_file_role(filename, facts)

            file_id = str(id_counter)
            id_counter += 1
            file_node_map[filename] = file_id

            display_name = filename.replace('.js', '').replace('.ts', '') \
                                   .replace('.py', '').replace('.java', '')
            node_label = f"{style['icon']} {display_name}\\n[{role_label}]"
            shape = role_shape(role, node_label)
            lines.append(f'    {file_id}{shape}')

            for cls in facts.get('classes', []):
                if not isinstance(cls, dict):
                    continue
                cls_type = cls.get('type', 'class')
                cls_id   = str(id_counter)
                id_counter += 1
                cls_label = cls['name']

                if cls_type == 'controller':
                    lines.append(f'    {cls_id}["{cls_label}"]')
                elif cls_type == 'service':
                    lines.append(f'    {cls_id}("{cls_label}")')
                elif cls_type == 'repository':
                    lines.append(f'    {cls_id}[/"{cls_label}"/]')
                elif cls_type == 'entity':
                    lines.append(f'    {cls_id}[("{cls_label}")]')
                else:
                    lines.append(f'    {cls_id}["{cls_label}"]')

                edges.append(f'    {file_id} --> {cls_id}')

                for method in cls.get('methods', [])[:MAX_METHODS_PER_CLASS]:
                    m_id = str(id_counter)
                    id_counter += 1
                    lines.append(f'    {m_id}("{method}")')
                    edges.append(f'    {cls_id} -->|method| {m_id}')

            if language in ['javascript', 'typescript', 'python']:
                funcs = facts.get('functions', [])[:MAX_FUNCTIONS_PER_FILE]
                for func in funcs:
                    func_id = str(id_counter)
                    id_counter += 1
                    lines.append(f'    {func_id}("{func}")')
                    edges.append(f'    {file_id} -->|defines| {func_id}')

            for req in facts.get('requires', []):
                if req.startswith('.'):
                    all_calls.append({'from_file': filename, 'to_file': req})

        lines.append("")

    lines.append("    %% File connections")
    seen_edges = set()

    for call in all_calls:
        from_file = call['from_file']
        to_path   = call['to_file']

        matched = None
        for known_file in file_node_map:
            known_stem = Path(known_file).stem.lower()
            to_stem    = Path(to_path).name.lower().replace('.js', '').replace('.ts', '')
            if known_stem == to_stem or to_stem in known_stem:
                matched = known_file
                break

        if matched and from_file in file_node_map:
            edge_key = f"{from_file}->{matched}"
            if edge_key not in seen_edges:
                seen_edges.add(edge_key)
                from_id = file_node_map[from_file]
                to_id   = file_node_map[matched]
                edges.append(f'    {from_id} -->|requires| {to_id}')

    lines.extend(edges)
    return "\n".join(lines)


# ── DESCRIPTION (legacy, used by --file mode) ─────────────────────────

def infer_project_domain(all_facts):
    combined = ''
    for facts_list in all_facts.values():
        for facts in facts_list:
            if not isinstance(facts, dict):
                continue
            combined += ' ' + facts.get('filename', '').lower()
            combined += ' ' + ' '.join(facts.get('functions', [])).lower()
            combined += ' ' + ' '.join(
                c['name'] for c in facts.get('classes', [])
                if isinstance(c, dict)
            ).lower()

    domains = {
        'University Management System':  ['student', 'professor', 'course', 'attendance',
                                           'enrollment', 'grade', 'faculty', 'semester'],
        'E-Commerce Platform':           ['cart', 'product', 'order', 'checkout', 'payment'],
        'Hospital Management System':    ['patient', 'doctor', 'appointment', 'prescription'],
        'Banking Application':           ['account', 'transaction', 'balance', 'transfer'],
        'Social Media Platform':         ['post', 'comment', 'like', 'follow', 'feed'],
        'Task Management Tool':          ['task', 'todo', 'ticket', 'kanban', 'sprint'],
        'Restaurant Management System':  ['menu', 'order', 'table', 'reservation', 'kitchen'],
        'Blog / CMS Platform':           ['blog', 'article', 'author', 'category', 'tag'],
    }

    best_match = None
    best_score = 0
    for name, keywords in domains.items():
        score = sum(1 for kw in keywords if kw in combined)
        if score > best_score:
            best_score = score
            best_match = name

    return best_match or 'Web Application', best_score


def generate_description(all_facts, cross_deps):
    languages   = list(all_facts.keys())
    total_files = sum(len(fl) for fl in all_facts.values())
    project_name, _ = infer_project_domain(all_facts)

    total_functions = sum(
        len(f.get('functions', []))
        for fl in all_facts.values()
        for f in fl if isinstance(f, dict)
    )
    total_classes = sum(
        len([c for c in f.get('classes', []) if isinstance(c, dict)])
        for fl in all_facts.values()
        for f in fl if isinstance(f, dict)
    )

    combined = ''
    for fl in all_facts.values():
        for f in fl:
            if not isinstance(f, dict):
                continue
            combined += ' ' + f.get('filename', '').lower()
            combined += ' ' + ' '.join(f.get('functions', [])).lower()
            combined += ' ' + ' '.join(f.get('requires', [])).lower()

    has_db    = any(w in combined for w in ['db', 'database', 'mongo', 'mysql',
                                              'postgres', 'sequelize', 'mongoose', 'sql'])
    has_email = any(w in combined for w in ['email', 'mail', 'nodemailer', 'smtp'])
    has_auth  = any(w in combined for w in ['auth', 'login', 'jwt', 'token', 'passport'])
    has_api   = any(w in combined for w in ['route', 'router', 'controller', 'endpoint', 'api'])

    desc = []
    desc.append("OVERVIEW")
    desc.append("-" * 40)
    desc.append(f"This is a {project_name}.")
    desc.append("")

    what_it_does = []
    if has_api:
        what_it_does.append("exposes API endpoints to handle client requests")
    if has_auth:
        what_it_does.append("manages user authentication and session security")
    if has_db:
        what_it_does.append("reads and writes data to a database")
    if has_email:
        what_it_does.append("sends automated email notifications")

    if what_it_does:
        desc.append("It " + ", ".join(what_it_does) + ".")
        desc.append("")

    desc.append(f"The codebase contains {total_files} backend files, "
                f"{total_functions} functions, and {total_classes} classes.")
    desc.append("")

    role_descriptions = {
        'controller':  'handles incoming HTTP requests and sends back responses',
        'service':     'contains the core business logic and processing rules',
        'repository':  'queries the database — reads, writes, updates, deletes data',
        'entity':      'represents a real-world object stored in the database',
        'validator':   'checks that incoming data is valid before processing it',
        'config':      'configures how the application starts and behaves',
        'middleware':  'intercepts every request to handle auth, logging, or validation',
        'database':    'manages the database connection used by the whole app',
        'router':      'maps incoming URLs to the right handler functions',
        'entry':       'the starting point — boots up the entire application',
        'utility':     'shared helper functions used across the project',
        'module':      'contains supporting logic for the application',
    }

    desc.append("COMPONENTS")
    desc.append("-" * 40)

    seen = set()
    for lang, facts_list in all_facts.items():
        style = LANGUAGE_STYLES.get(lang, {'icon': '📄'})
        icon  = style['icon']

        for facts in facts_list[:MAX_FILES_PER_LANGUAGE]:
            if not isinstance(facts, dict):
                continue
            if not has_renderable_content(facts):
                continue

            filename = facts.get('filename', 'unknown')
            if filename in seen:
                continue
            seen.add(filename)

            role, role_label = detect_file_role(filename, facts)
            funcs   = facts.get('functions', [])
            classes = [c for c in facts.get('classes', []) if isinstance(c, dict)]

            if classes:
                for cls in classes[:2]:
                    cls_type = cls.get('type', 'class')
                    methods  = cls.get('methods', [])
                    role_desc = role_descriptions.get(role, 'contains application logic')

                    desc.append(f"  {icon} {filename}")
                    desc.append(f"     Role: {role_label} — {role_desc}")

                    anns = cls.get('annotations', [])
                    if anns:
                        desc.append(f"     Annotations: @{'  @'.join(anns[:4])}")

                    deps = cls.get('dependencies', [])
                    if deps:
                        desc.append(f"     Injects: {', '.join(deps[:4])}")

                    if methods:
                        desc.append(f"     Operations: {', '.join(methods[:6])}")

                    desc.append("")

            elif funcs:
                role_desc = role_descriptions.get(role, 'contains application logic')
                desc.append(f"  {icon} {filename}")
                desc.append(f"     Role: {role_label} — {role_desc}")
                desc.append(f"     Functions: {', '.join(funcs[:6])}")
                desc.append("")

    desc.append("ARCHITECTURE PATTERN")
    desc.append("-" * 40)

    roles_present = set()
    for fl in all_facts.values():
        for f in fl:
            if not isinstance(f, dict):
                continue
            role, _ = detect_file_role(f.get('filename', ''), f)
            roles_present.add(role)

    has_spring = any(
        facts.get('spring_patterns', {}).get('controllers')
        for fl in all_facts.values()
        for facts in fl if isinstance(facts, dict)
    )

    if has_spring:
        desc.append("Pattern: MVC (Model-View-Controller) via Spring Boot")
        desc.append("")
        desc.append("  HTTP Request → Controller → Service → Repository → Database")
    elif {'router', 'service', 'database'}.issubset(roles_present):
        desc.append("Pattern: Layered Node.js Backend (Router → Service → Database)")
        desc.append("")
        desc.append("  HTTP Request → app.js → Router → Service → DB")
    elif 'python' in languages:
        desc.append("Pattern: Python Backend Service")
    else:
        desc.append("Pattern: Modular Backend")

    desc.append("")
    return "\n".join(desc)


# ── RENDER ────────────────────────────────────────────────────────────

def render_multi_language(all_facts, project_name="Project"):
    """Legacy renderer — used by --file mode. Folder/GitHub now use render_ai_diagram."""
    print("\n" + "=" * 60)
    print(f"HIRO Analysis: {project_name}")
    print("=" * 60)

    if not isinstance(all_facts, dict):
        print(f"✗ Error: Expected dict, got {type(all_facts)}")
        return

    mermaid_code = build_mermaid_multi_language(all_facts)
    description  = generate_description(all_facts, {})

    print("=== MERMAID CODE ===")
    print(mermaid_code)
    print()
    print("=== DESCRIPTION ===")
    print(description)
    print()
    print("=" * 60)
    print("Analysis complete.")
    print("=" * 60)


def render_single_file(facts):
    if not isinstance(facts, dict):
        print(f"✗ Error: Expected facts dict, got {type(facts)}")
        return
    all_facts = {facts['language']: [facts]}
    render_multi_language(all_facts, facts.get('filename', 'unknown'))
