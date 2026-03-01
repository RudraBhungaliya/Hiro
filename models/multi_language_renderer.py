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
    funcs   = ' '.join(facts.get('functions', [])).lower()
    classes = [c for c in facts.get('classes', []) if isinstance(c, dict)]
    class_names = ' '.join(c['name'] for c in classes).lower()
    combined = name + ' ' + funcs + ' ' + class_names

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
    if any(w in combined for w in ['db', 'database', 'connection', 'pool', 'mongo', 'mysql', 'postgres', 'sequelize', 'mongoose']):
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
    if any(w in combined for w in ['hints', 'runtime']):
        return 'config', 'Runtime Config'
    if any(w in combined for w in ['welcome', 'crash', 'web']):
        return 'controller', 'Controller'
    if any(w in combined for w in ['base', 'named', 'person', 'abstract']):
        return 'entity', 'Base Entity'
    if any(w in combined for w in ['pet', 'owner', 'vet', 'visit', 'specialty']):
        return 'entity', 'Domain Entity'

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


# ── DIAGRAM BUILDER ───────────────────────────────────────────────────

def build_mermaid_multi_language(all_facts):
    lines = ["graph TD"]
    lines.append("")
    edges = []

    id_counter   = 1
    file_node_map = {}  # filename -> node_id
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

            # File node
            file_id = str(id_counter)
            id_counter += 1
            file_node_map[filename] = file_id

            display_name = filename.replace('.js','').replace('.ts','') \
                                   .replace('.py','').replace('.java','')
            node_label = f"{style['icon']} {display_name}\\n[{role_label}]"
            shape = role_shape(role, node_label)
            lines.append(f'    {file_id}{shape}')

            # Java Spring — classes as child nodes
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

                # Methods on class
                for method in cls.get('methods', [])[:MAX_METHODS_PER_CLASS]:
                    m_id = str(id_counter)
                    id_counter += 1
                    lines.append(f'    {m_id}("{method}")')
                    edges.append(f'    {cls_id} -->|method| {m_id}')

            # JS/Python — key functions as child nodes
            if language in ['javascript', 'typescript', 'python']:
                funcs = facts.get('functions', [])[:MAX_FUNCTIONS_PER_FILE]
                for func in funcs:
                    func_id = str(id_counter)
                    id_counter += 1
                    lines.append(f'    {func_id}("{func}")')
                    edges.append(f'    {file_id} -->|defines| {func_id}')

            # Collect require() calls for cross-file edges
            for req in facts.get('requires', []):
                if req.startswith('.'):
                    all_calls.append({
                        'from_file': filename,
                        'to_file':   req
                    })

        lines.append("")

    # Cross-file edges from require()
    lines.append("    %% File connections")
    seen_edges = set()

    for call in all_calls:
        from_file = call['from_file']
        to_path   = call['to_file']

        # Match to_path against known filenames
        matched = None
        for known_file in file_node_map:
            known_stem = Path(known_file).stem.lower()
            to_stem    = Path(to_path).name.lower().replace('.js','').replace('.ts','')
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


# ── DESCRIPTION ───────────────────────────────────────────────────────

def infer_project_domain(all_facts):
    """Guess what the project is about from filenames and function names."""
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
        'University Management System':  ['student', 'professor', 'course', 'attendance', 'enrollment', 'grade', 'faculty', 'semester', 'university'],
        'E-Commerce Platform':           ['cart', 'product', 'order', 'checkout', 'payment', 'invoice', 'shop'],
        'Hospital Management System':    ['patient', 'doctor', 'appointment', 'prescription', 'medical', 'clinic'],
        'Banking Application':           ['account', 'transaction', 'balance', 'transfer', 'loan', 'deposit'],
        'Social Media Platform':         ['post', 'comment', 'like', 'follow', 'feed', 'friend', 'message'],
        'Task Management Tool':          ['task', 'todo', 'ticket', 'kanban', 'board', 'sprint'],
        'Restaurant Management System':  ['menu', 'order', 'table', 'reservation', 'food', 'kitchen'],
        'Blog / CMS Platform':           ['blog', 'article', 'author', 'category', 'tag', 'content'],
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
    languages    = list(all_facts.keys())
    total_files  = sum(len(fl) for fl in all_facts.values())
    project_name, domain_score = infer_project_domain(all_facts)

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

    # Detect capabilities
    combined = ''
    for fl in all_facts.values():
        for f in fl:
            if not isinstance(f, dict):
                continue
            combined += ' ' + f.get('filename', '').lower()
            combined += ' ' + ' '.join(f.get('functions', [])).lower()
            combined += ' ' + ' '.join(f.get('requires', [])).lower()

    has_db    = any(w in combined for w in ['db', 'database', 'mongo', 'mysql', 'postgres', 'sequelize', 'mongoose', 'sql'])
    has_email = any(w in combined for w in ['email', 'mail', 'nodemailer', 'smtp'])
    has_auth  = any(w in combined for w in ['auth', 'login', 'jwt', 'token', 'passport', 'session'])
    has_api   = any(w in combined for w in ['route', 'router', 'controller', 'endpoint', 'api'])

    desc = []

    # ── 1. OVERVIEW ───────────────────────────────────────────
    desc.append("OVERVIEW")
    desc.append("-" * 40)

    desc.append(f"This is a {project_name}.")
    desc.append("")

    # Build one solid paragraph about what it does
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

    # ── 2. COMPONENTS ─────────────────────────────────────────
    # ── 2. COMPONENTS ─────────────────────────────────────────
    desc.append("COMPONENTS")
    desc.append("-" * 40)

    # Role descriptions — specific per role
    role_descriptions = {
        'controller':  'handles incoming HTTP requests and sends back responses',
        'service':     'contains the core business logic and processing rules',
        'repository':  'queries the database — reads, writes, updates, deletes data',
        'entity':      'represents a real-world object stored in the database',
        'validator':   'checks that incoming data is valid before processing it',
        'formatter':   'converts data between formats for display or storage',
        'config':      'configures how the application starts and behaves',
        'middleware':  'intercepts every request to handle auth, logging, or validation',
        'database':    'manages the database connection used by the whole app',
        'router':      'maps incoming URLs to the right handler functions',
        'entry':       'the starting point — boots up the entire application',
        'utility':     'shared helper functions used across the project',
        'module':      'contains supporting logic for the application',
    }

    # Java class type descriptions
    java_type_descriptions = {
        'controller': 'receives HTTP requests from the client and decides what to do with them',
        'service':    'applies business rules — the brain of the application',
        'repository': 'speaks directly to the database on behalf of the service layer',
        'entity':     'a data model that maps directly to a database table',
        'class':      'contains application logic',
    }

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
                    cls_type    = cls.get('type', 'class')
                    methods     = cls.get('methods', [])
                    annotations = cls.get('annotations', [])

                    # Pick most specific description
                    if lang == 'java':
                        role_desc = java_type_descriptions.get(cls_type, 'contains application logic')
                    else:
                        role_desc = role_descriptions.get(role, 'contains application logic')

                    desc.append(f"  {icon} {filename}")
                    desc.append(f"     Role: {role_label} — {role_desc}")

                    if annotations:
                        desc.append(f"     Annotations: @{'  @'.join(annotations[:4])}")

                    if methods:
                        # Give plain English names where possible
                        method_summary = ', '.join(methods[:6])
                        desc.append(f"     Operations: {method_summary}")

                    # Specific domain knowledge
                    name_lower = filename.lower()
                    if 'owner' in name_lower:
                        desc.append(f"     Manages pet owners — their details, pets, and visit history.")
                    elif 'pet' in name_lower and 'type' not in name_lower:
                        desc.append(f"     Manages pets — their type, birth date, and associated visits.")
                    elif 'vet' in name_lower:
                        desc.append(f"     Manages vets — their specialties and profile information.")
                    elif 'visit' in name_lower:
                        desc.append(f"     Manages visits — when a pet came in and what was noted.")
                    elif 'specialty' in name_lower:
                        desc.append(f"     Represents a medical specialty a vet can have.")
                    elif 'student' in name_lower:
                        desc.append(f"     Manages student data and operations.")
                    elif 'professor' in name_lower:
                        desc.append(f"     Manages professor data and operations.")
                    elif 'course' in name_lower:
                        desc.append(f"     Manages course data and enrollment.")
                    elif 'welcome' in name_lower:
                        desc.append(f"     Serves the home/welcome page of the application.")
                    elif 'crash' in name_lower:
                        desc.append(f"     A test controller that intentionally triggers errors for debugging.")
                    elif 'cache' in name_lower:
                        desc.append(f"     Configures caching to speed up repeated database lookups.")
                    elif 'web' in name_lower and 'config' in name_lower.replace('web',''):
                        desc.append(f"     Configures web settings like locale, interceptors, and URL mapping.")
                    elif 'base' in name_lower or 'named' in name_lower or 'person' in name_lower:
                        desc.append(f"     A base class — other domain classes inherit common fields from this.")
                    elif 'hint' in name_lower or 'runtime' in name_lower:
                        desc.append(f"     Provides runtime configuration hints for optimized deployment.")
                    elif 'application' in name_lower:
                        desc.append(f"     The main entry point — this is what starts the entire application.")

                    desc.append("")

            elif funcs:
                role_desc = role_descriptions.get(role, 'contains application logic')
                desc.append(f"  {icon} {filename}")
                desc.append(f"     Role: {role_label} — {role_desc}")
                desc.append(f"     Functions: {', '.join(funcs[:6])}")

                # JS file domain hints
                name_lower = filename.lower()
                if 'email' in name_lower or 'mail' in name_lower:
                    desc.append(f"     Sends automated emails — attendance alerts, notifications, reminders.")
                elif 'db' in name_lower or 'database' in name_lower:
                    desc.append(f"     Opens and manages the database connection for the whole application.")
                elif 'route' in name_lower:
                    desc.append(f"     Defines the API URL paths and links them to controller functions.")
                elif 'controller' in name_lower:
                    desc.append(f"     Handles specific API requests and calls the right service or query.")
                elif 'quer' in name_lower:
                    desc.append(f"     Contains all SQL queries — the raw database read/write operations.")
                elif 'server' in name_lower or 'app' in name_lower:
                    desc.append(f"     Starts the server, loads middleware, and registers all routes.")
                elif 'script' in name_lower:
                    desc.append(f"     Frontend script — handles UI interactions in the browser.")

                desc.append("")

    # ── 3. ARCHITECTURE PATTERN ───────────────────────────────
    desc.append("ARCHITECTURE PATTERN")
    desc.append("-" * 40)

    # Detect pattern from roles present
    roles_present = set()
    for fl in all_facts.values():
        for f in fl:
            if not isinstance(f, dict):
                continue
            role, _ = detect_file_role(f.get('filename', ''), f)
            roles_present.add(role)

    has_java     = 'java' in languages
    has_spring   = any(
        facts.get('spring_patterns', {}).get('controllers')
        for fl in all_facts.values()
        for facts in fl if isinstance(facts, dict)
    )

    if has_spring:
        desc.append("Pattern: MVC (Model-View-Controller) via Spring Boot")
        desc.append("")
        desc.append("  HTTP Request")
        desc.append("       │")
        desc.append("       ▼")
        desc.append("  ┌────────────┐     ┌─────────┐     ┌────────────┐     ┌──────────┐")
        desc.append("  │ Controller │────▶│ Service │────▶│ Repository │────▶│ Database │")
        desc.append("  └────────────┘     └─────────┘     └────────────┘     └──────────┘")
        desc.append("")
        desc.append("  Controller  — handles incoming requests, validates input")
        desc.append("  Service     — applies business rules and logic")
        desc.append("  Repository  — talks to the database")

    elif {'router', 'service', 'database'}.issubset(roles_present) or \
         {'router', 'database'}.issubset(roles_present):
        desc.append("Pattern: Layered Node.js Backend (Router → Service → Database)")
        desc.append("")
        desc.append("  HTTP Request")
        desc.append("       │")
        desc.append("       ▼")
        if 'entry' in roles_present:
            desc.append("  ┌──────────┐")
            desc.append("  │  app.js  │  (entry point — starts the server)")
            desc.append("  └──────────┘")
            desc.append("       │")
            desc.append("       ▼")
        desc.append("  ┌──────────┐     ┌─────────┐     ┌──────────┐")
        desc.append("  │  Router  │────▶│ Service │────▶│    DB    │")
        desc.append("  └──────────┘     └─────────┘     └──────────┘")
        if 'middleware' in roles_present:
            desc.append("")
            desc.append("  Middleware sits across all layers handling auth / validation.")
        if has_email:
            desc.append("")
            desc.append("  Email Service sends notifications triggered by business events.")

    elif 'python' in languages:
        desc.append("Pattern: Python Backend Service")
        desc.append("")
        desc.append("  Input ──▶ Business Logic ──▶ Output / Database")

    else:
        desc.append("Pattern: Modular Backend")
        desc.append("")
        desc.append("  Files are organized as independent modules,")
        desc.append("  each responsible for a specific part of the system.")

    desc.append("")

    return "\n".join(desc)


# ── RENDER ────────────────────────────────────────────────────────────

def render_multi_language(all_facts, project_name="Project"):
    print("\n" + "=" * 60)
    print(f"HIRO Analysis: {project_name}")
    print("=" * 60)

    if not isinstance(all_facts, dict):
        print(f"✗ Error: Expected dict, got {type(all_facts)}")
        return

    cross_deps   = {}
    mermaid_code = build_mermaid_multi_language(all_facts)
    description  = generate_description(all_facts, cross_deps)

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