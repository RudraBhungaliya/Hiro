"""
Multi-Language Renderer - Terminal Output Only
"""

LANGUAGE_STYLES = {
    'python': {'color': '#3776ab', 'icon': '🐍'},
    'java': {'color': '#007396', 'icon': '☕'},
    'javascript': {'color': '#f7df1e', 'icon': '⚡'},
    'typescript': {'color': '#3178c6', 'icon': '📘'},
    'tsx': {'color': '#61dafb', 'icon': '⚛️'},
    'html': {'color': '#e34c26', 'icon': '🌐'},
    'css': {'color': '#563d7c', 'icon': '🎨'}
}

MAX_FILES_PER_LANGUAGE = 60
MAX_METHODS_PER_CLASS = 5
MAX_FUNCTIONS_PER_FILE = 5


def detect_cross_language_dependencies(all_facts):
    cross_deps = []

    html_files = all_facts.get('html', [])
    js_files = all_facts.get('javascript', []) + all_facts.get('typescript', [])

    for html_facts in html_files:
        if not isinstance(html_facts, dict):
            continue
        for script_src in html_facts.get('scripts', []):
            if script_src == 'inline_script':
                continue
            for js_facts in js_files:
                if not isinstance(js_facts, dict):
                    continue
                if script_src in js_facts['filename'] or js_facts['filename'] in script_src:
                    cross_deps.append({
                        'from': html_facts['filename'],
                        'to': js_facts['filename'],
                        'type': 'loads script'
                    })

    for html_facts in html_files:
        if not isinstance(html_facts, dict):
            continue
        for stylesheet_href in html_facts.get('stylesheets', []):
            for css_facts in all_facts.get('css', []):
                if not isinstance(css_facts, dict):
                    continue
                if stylesheet_href in css_facts['filename']:
                    cross_deps.append({
                        'from': html_facts['filename'],
                        'to': css_facts['filename'],
                        'type': 'loads styles'
                    })

    return cross_deps


def has_renderable_content(facts):
    if not isinstance(facts, dict):
        return False
    return any([
        facts.get('classes'),
        facts.get('components'),
        facts.get('functions'),
        facts.get('structure'),
        facts.get('scripts'),
        facts.get('stylesheets'),
        facts.get('forms'),
        facts.get('ids'),
        facts.get('animations'),
        facts.get('selectors'),
        facts.get('properties'),
        facts.get('all_tags'),
        facts.get('links'),
        facts.get('titles'),
        facts.get('spring_patterns', {}).get('controllers')
    ])


def build_mermaid_multi_language(all_facts):
    lines = ["graph TD"]
    lines.append("")

    id_counter = 1
    edges = []

    for language, facts_list in all_facts.items():
        if not facts_list:
            continue

        facts_list = facts_list[:MAX_FILES_PER_LANGUAGE]

        if not any(has_renderable_content(f) for f in facts_list):
            continue

        style = LANGUAGE_STYLES.get(language, {'color': '#666666', 'icon': '📄'})
        lines.append(f"    %% {language.upper()} files")

        seen_functions = {}
        seen_classes = {}
        seen_components = {}
        seen_files = {}       # filename -> node_id
        seen_css_files = {}   # filename -> node_id for CSS
        seen_html_files = {}  # filename -> node_id for HTML
        all_calls = []

        for facts in facts_list:
            if not isinstance(facts, dict):
                continue
            if not has_renderable_content(facts):
                continue

            filename = facts.get('filename', 'unknown')

            # --- JAVASCRIPT / PYTHON / JAVA ---
            # Create a file node, then connect functions/classes to it
            if language in ['javascript', 'typescript', 'tsx', 'python', 'java']:

                has_functions = bool(facts.get('functions'))
                has_classes = bool(facts.get('classes'))
                has_components = bool(facts.get('components'))

                if has_functions or has_classes or has_components:
                    # File node
                    if filename not in seen_files:
                        file_id = str(id_counter)
                        id_counter += 1
                        seen_files[filename] = file_id
                        lines.append(f'    {file_id}["{style["icon"]} {filename}"]')

                    file_id = seen_files[filename]

                    # Classes → connect to file
                    for cls in facts.get('classes', []):
                        if not isinstance(cls, dict):
                            continue
                        cls_name = cls['name']
                        if cls_name in seen_classes:
                            continue
                        class_id = str(id_counter)
                        id_counter += 1
                        seen_classes[cls_name] = class_id
                        lines.append(f'    {class_id}["{cls_name}"]')
                        edges.append(f'    {file_id} -->|contains| {class_id}')

                        for method in cls.get('methods', [])[:MAX_METHODS_PER_CLASS]:
                            method_id = str(id_counter)
                            id_counter += 1
                            lines.append(f'    {method_id}("{method}")')
                            edges.append(f'    {class_id} -->|has method| {method_id}')

                    # Components → connect to file
                    for comp in facts.get('components', []):
                        if not isinstance(comp, dict):
                            continue
                        comp_name = comp['name']
                        if comp_name in seen_components:
                            continue
                        comp_id = str(id_counter)
                        id_counter += 1
                        seen_components[comp_name] = comp_id
                        lines.append(f'    {comp_id}(("{comp_name}"))')
                        edges.append(f'    {file_id} -->|contains| {comp_id}')

                    # Functions → connect to file
                    for func in facts.get('functions', [])[:MAX_FUNCTIONS_PER_FILE]:
                        if func in seen_functions:
                            continue
                        func_id = str(id_counter)
                        id_counter += 1
                        seen_functions[func] = func_id
                        lines.append(f'    {func_id}("{func}")')
                        edges.append(f'    {file_id} -->|defines| {func_id}')

                # Collect calls
                for call in facts.get('calls', []):
                    all_calls.append(call)

            # --- HTML ---
            elif language == 'html':
                has_html_content = any([
                    facts.get('structure'),
                    facts.get('scripts'),
                    facts.get('stylesheets'),
                    facts.get('forms'),
                    facts.get('titles')
                ])

                if has_html_content and filename not in seen_html_files:
                    html_file_id = str(id_counter)
                    id_counter += 1
                    seen_html_files[filename] = html_file_id
                    lines.append(f'    {html_file_id}["🌐 {filename}"]')

                    if filename in seen_html_files:
                        html_file_id = seen_html_files[filename]

                        for title in facts.get('titles', []):
                            t_id = str(id_counter)
                            id_counter += 1
                            lines.append(f'    {t_id}["title: {title}"]')
                            edges.append(f'    {html_file_id} -->|has| {t_id}')

                        for script in facts.get('scripts', []):
                            s_id = str(id_counter)
                            id_counter += 1
                            label = 'inline script' if script == 'inline_script' else f'script: {script}'
                            lines.append(f'    {s_id}["📜 {label}"]')
                            edges.append(f'    {html_file_id} -->|loads| {s_id}')

                        for href in facts.get('stylesheets', []):
                            sh_id = str(id_counter)
                            id_counter += 1
                            lines.append(f'    {sh_id}["🎨 {href}"]')
                            edges.append(f'    {html_file_id} -->|styles| {sh_id}')

                        for form in facts.get('forms', []):
                            f_id = str(id_counter)
                            id_counter += 1
                            action = form.get('action', '/')
                            method = form.get('method', 'GET')
                            lines.append(f'    {f_id}["form {method}: {action}"]')
                            edges.append(f'    {html_file_id} -->|has form| {f_id}')

            # --- CSS ---
            elif language == 'css':
                has_css_content = any([
                    facts.get('classes'),
                    facts.get('ids'),
                    facts.get('selectors'),
                    facts.get('animations')
                ])

                if has_css_content and filename not in seen_css_files:
                    css_file_id = str(id_counter)
                    id_counter += 1
                    seen_css_files[filename] = css_file_id
                    lines.append(f'    {css_file_id}["🎨 {filename}"]')

                    # Selectors → connect to CSS file
                    for sel in facts.get('selectors', [])[:8]:
                        sel_id = str(id_counter)
                        id_counter += 1
                        lines.append(f'    {sel_id}["{sel}"]')
                        edges.append(f'    {css_file_id} -->|styles| {sel_id}')

                    for cls_name in facts.get('classes', [])[:8]:
                        if isinstance(cls_name, str):
                            cls_id = str(id_counter)
                            id_counter += 1
                            lines.append(f'    {cls_id}[".{cls_name}"]')
                            edges.append(f'    {css_file_id} -->|styles| {cls_id}')

                    for id_name in facts.get('ids', [])[:5]:
                        id_node = str(id_counter)
                        id_counter += 1
                        lines.append(f'    {id_node}["#{id_name}"]')
                        edges.append(f'    {css_file_id} -->|styles| {id_node}')

                    for anim in facts.get('animations', []):
                        anim_id = str(id_counter)
                        id_counter += 1
                        lines.append(f'    {anim_id}["@keyframes {anim}"]')
                        edges.append(f'    {css_file_id} -->|animation| {anim_id}')

        # Second pass — cross-function call edges
        seen_edges = set()
        for call in all_calls:
            from_name = call.get('from')
            to_name = call.get('to')
            if from_name in seen_functions and to_name in seen_functions:
                edge_key = f"{from_name}->{to_name}"
                if edge_key not in seen_edges:
                    seen_edges.add(edge_key)
                    edges.append(f'    {seen_functions[from_name]} -->|calls| {seen_functions[to_name]}')

        lines.append("")

    if edges:
        lines.append("    %% Edges")
        lines.extend(edges)

    return "\n".join(lines)


def generate_description(all_facts, cross_deps):
    total_files = sum(len(facts_list) for facts_list in all_facts.values())
    languages = list(all_facts.keys())

    description = []

    # ── OVERVIEW ──────────────────────────────────────────────
    description.append("=" * 60)
    description.append("PROJECT OVERVIEW")
    description.append("=" * 60)

    # Count everything
    total_js_files   = len(all_facts.get('javascript', []) + all_facts.get('typescript', []) + all_facts.get('tsx', []))
    total_html_files = len(all_facts.get('html', []))
    total_css_files  = len(all_facts.get('css', []))
    total_java_files = len(all_facts.get('java', []))
    total_py_files   = len(all_facts.get('python', []))

    total_functions  = sum(len(f.get('functions', [])) for fl in all_facts.values() for f in fl if isinstance(f, dict))
    total_classes    = sum(len([c for c in f.get('classes', []) if isinstance(c, dict)]) for fl in all_facts.values() for f in fl if isinstance(f, dict))
    total_components = sum(len(f.get('components', [])) for fl in all_facts.values() for f in fl if isinstance(f, dict))

    # Determine project type in plain English
    if total_html_files > 0 and (total_js_files > 0 or total_css_files > 0):
        project_type = "a website"
        project_explanation = (
            "This is a website project. It has web pages (HTML files) that users see in their browser, "
            "stylesheets (CSS files) that control how everything looks — colors, fonts, layout — "
            "and JavaScript files that make things interactive, like buttons, animations, and menus."
        )
    elif total_js_files > 0 and total_html_files == 0:
        project_type = "a JavaScript application"
        project_explanation = (
            "This is a JavaScript application — a program written in JavaScript that runs either "
            "in a web browser or on a server. It contains logic, functions, and components that "
            "work together to deliver a feature or service."
        )
    elif total_java_files > 0:
        project_type = "a Java backend application"
        project_explanation = (
            "This is a backend application written in Java. It runs on a server and handles things "
            "like processing requests from users, talking to a database, and sending back responses. "
            "Users never see this code directly — it powers what happens behind the scenes."
        )
    elif total_py_files > 0:
        project_type = "a Python application"
        project_explanation = (
            "This is a Python application. Python is used for many things — web servers, data processing, "
            "automation, and AI. This project uses Python to handle its core logic and functionality."
        )
    else:
        project_type = "a software project"
        project_explanation = "This is a software project containing multiple files that work together."

    description.append(f"In simple terms, this is {project_type}.")
    description.append("")
    description.append(project_explanation)
    description.append("")
    description.append(f"At a glance:")
    description.append(f"  • Total files: {total_files}")
    if total_html_files:  description.append(f"  • Web pages (HTML):      {total_html_files} file(s)")
    if total_css_files:   description.append(f"  • Stylesheets (CSS):     {total_css_files} file(s)")
    if total_js_files:    description.append(f"  • JavaScript logic:      {total_js_files} file(s)")
    if total_java_files:  description.append(f"  • Java code:             {total_java_files} file(s)")
    if total_py_files:    description.append(f"  • Python code:           {total_py_files} file(s)")
    if total_functions:   description.append(f"  • Functions (tasks):     {total_functions}")
    if total_classes:     description.append(f"  • Classes (blueprints):  {total_classes}")
    if total_components:  description.append(f"  • UI Components:         {total_components}")

    # ── WHAT EACH FILE DOES ───────────────────────────────────
    description.append("")
    description.append("=" * 60)
    description.append("WHAT EACH FILE DOES")
    description.append("=" * 60)
    description.append(
        "Think of each file like a room in a house — each one has "
        "a specific purpose and they all work together."
    )
    description.append("")

    seen_filenames = set()

    for lang, facts_list in all_facts.items():
        style = LANGUAGE_STYLES.get(lang, {})
        icon  = style.get('icon', '📄')

        for facts in facts_list[:MAX_FILES_PER_LANGUAGE]:
            if not isinstance(facts, dict):
                continue
            if not has_renderable_content(facts):
                continue

            filename = facts.get('filename', 'unknown')
            if filename in seen_filenames:
                continue
            seen_filenames.add(filename)

            description.append(f"  {icon} {filename}")

            # Plain English explanation by language
            if lang in ['javascript', 'typescript', 'tsx']:
                funcs      = facts.get('functions', [])
                components = facts.get('components', [])
                classes    = [c for c in facts.get('classes', []) if isinstance(c, dict)]
                hooks      = facts.get('hooks', [])
                requires   = facts.get('requires', [])

                if components:
                    names = ', '.join(c['name'] for c in components[:4])
                    description.append(f"     This file builds visual pieces of the webpage called components.")
                    description.append(f"     Components found: {names}")
                    description.append(f"     Think of components like LEGO blocks — each one is a reusable piece of the UI.")

                if classes:
                    names = ', '.join(c['name'] for c in classes[:4])
                    description.append(f"     This file defines blueprints called classes: {names}")
                    description.append(f"     A class is like a template — it describes how something should behave.")

                if funcs:
                    description.append(f"     This file contains {len(funcs)} function(s) — small tasks the program can run.")
                    description.append(f"     Functions found: {', '.join(funcs[:5])}")
                    description.append(f"     Each function is like a recipe — it takes some input and produces a result.")

                if hooks:
                    description.append(f"     It uses React hooks ({', '.join(hooks[:4])}) to manage things like")
                    description.append(f"     storing data, reacting to changes, and fetching information.")

                if requires:
                    external = [r for r in requires if not r.startswith('.')]
                    internal = [r for r in requires if r.startswith('.')]
                    if external:
                        description.append(f"     It relies on external tools/libraries: {', '.join(external[:4])}")
                    if internal:
                        description.append(f"     It connects to other files in the project: {', '.join(internal[:4])}")

                if not funcs and not components and not classes:
                    description.append(f"     This is a JavaScript file with supporting logic for the application.")

            elif lang == 'html':
                titles      = facts.get('titles', [])
                scripts     = [s for s in facts.get('scripts', []) if s != 'inline_script']
                stylesheets = facts.get('stylesheets', [])
                forms       = facts.get('forms', [])
                structure   = facts.get('structure', [])

                description.append(f"     This is a web page — what users actually see when they open the site in a browser.")

                if titles:
                    description.append(f"     Page title: \"{titles[0]}\"")

                if structure:
                    description.append(f"     It is structured with sections like: {', '.join(set(structure[:6]))}")

                if stylesheets:
                    description.append(f"     It loads its visual design from: {', '.join(stylesheets[:3])}")

                if scripts:
                    description.append(f"     It loads interactive behaviour from: {', '.join(scripts[:3])}")

                if forms:
                    description.append(f"     It contains {len(forms)} form(s) — areas where users can type and submit information.")

                if not scripts and not stylesheets:
                    description.append(f"     This page contains the raw structure and content of a webpage.")

            elif lang == 'css':
                selectors  = facts.get('selectors', [])
                classes    = [c for c in facts.get('classes', []) if isinstance(c, str)]
                ids        = facts.get('ids', [])
                animations = facts.get('animations', [])
                queries    = facts.get('media_queries', [])

                description.append(f"     This is a stylesheet — it controls how the website looks.")
                description.append(f"     Think of it as the interior design of the website: colors, fonts, spacing, layout.")

                if selectors:
                    description.append(f"     It styles these HTML elements: {', '.join(selectors[:6])}")

                if classes:
                    description.append(f"     It has {len(classes)} style class(es) like: {', '.join(classes[:5])}")
                    description.append(f"     Style classes are reusable looks you can apply to any element.")

                if ids:
                    description.append(f"     It styles specific unique elements: {', '.join(ids[:4])}")

                if animations:
                    description.append(f"     It includes animations: {', '.join(animations[:4])}")
                    description.append(f"     Animations make elements move or change smoothly on screen.")

                if queries:
                    description.append(f"     It adapts the design for different screen sizes (mobile, tablet, desktop).")

            elif lang == 'python':
                funcs   = facts.get('functions', [])
                classes = [c for c in facts.get('classes', []) if isinstance(c, dict)]

                description.append(f"     This is a Python file — it contains logic that runs on the server.")

                if classes:
                    for cls in classes[:3]:
                        methods = cls.get('methods', [])
                        description.append(f"     It defines '{cls['name']}' — a blueprint with {len(methods)} action(s): {', '.join(methods[:4])}")

                if funcs:
                    description.append(f"     It can perform {len(funcs)} task(s): {', '.join(funcs[:5])}")

            elif lang == 'java':
                classes = [c for c in facts.get('classes', []) if isinstance(c, dict)]
                spring  = facts.get('spring_patterns', {})

                description.append(f"     This is a Java file — part of the backend server logic.")

                for cls in classes[:3]:
                    cls_type = cls.get('type', 'class')
                    methods  = cls.get('methods', [])

                    if cls_type == 'controller':
                        description.append(f"     '{cls['name']}' is a Controller — it receives requests from users")
                        description.append(f"     (like clicking a button) and decides what to do with them.")
                    elif cls_type == 'service':
                        description.append(f"     '{cls['name']}' is a Service — it contains the core business logic,")
                        description.append(f"     like calculating, processing, or applying rules.")
                    elif cls_type == 'repository':
                        description.append(f"     '{cls['name']}' is a Repository — it talks to the database,")
                        description.append(f"     fetching and saving data.")
                    elif cls_type == 'entity':
                        description.append(f"     '{cls['name']}' is an Entity — it represents a real-world object")
                        description.append(f"     stored in the database, like a User or an Order.")
                    else:
                        description.append(f"     '{cls['name']}' handles: {', '.join(methods[:4])}")

            description.append("")

    # ── HOW FILES CONNECT ─────────────────────────────────────
    if cross_deps:
        description.append("=" * 60)
        description.append("HOW FILES CONNECT TO EACH OTHER")
        description.append("=" * 60)
        description.append("Just like a TV plugs into a power socket, files depend on each other.")
        description.append("")
        for dep in cross_deps:
            if dep['type'] == 'loads script':
                description.append(f"  • {dep['from']} uses the JavaScript logic from {dep['to']}")
            elif dep['type'] == 'loads styles':
                description.append(f"  • {dep['from']} gets its visual design from {dep['to']}")
            else:
                description.append(f"  • {dep['from']} → {dep['to']} ({dep['type']})")
        description.append("")

    # ── ARCHITECTURE ──────────────────────────────────────────
    description.append("=" * 60)
    description.append("ARCHITECTURE — THE BIG PICTURE")
    description.append("=" * 60)

    if 'javascript' in languages or 'typescript' in languages:
        if 'python' in languages or 'java' in languages:
            description.append("This is a FULL-STACK application.")
            description.append("")
            description.append("  FRONTEND (what users see):")
            description.append("    HTML → the structure, like the skeleton of a webpage")
            description.append("    CSS  → the styling, like clothes and makeup")
            description.append("    JS   → the behaviour, like muscles that make things move")
            description.append("")
            description.append("  BACKEND (what runs on the server):")
            if 'java' in languages:
                description.append("    Java → handles requests, business logic, and database access")
            if 'python' in languages:
                description.append("    Python → handles requests, processing, and data")
        elif total_html_files > 0:
            description.append("This is a FRONTEND WEB APPLICATION.")
            description.append("")
            description.append("  It runs entirely in the user's browser.")
            description.append("  HTML gives it structure, CSS makes it look good,")
            description.append("  and JavaScript makes it interactive and dynamic.")
        else:
            description.append("This is a NODE.JS / JAVASCRIPT APPLICATION.")
            description.append("")
            description.append("  It runs on a server using JavaScript.")
            description.append("  This is uncommon — JavaScript usually runs in browsers,")
            description.append("  but Node.js lets it run as a backend server too.")
    elif 'java' in languages:
        description.append("This is a JAVA BACKEND APPLICATION.")
        description.append("")
        description.append("  It runs on a server. Users interact with it through a frontend")
        description.append("  (not included here). It likely follows the MVC pattern:")
        description.append("    Controller → receives the request")
        description.append("    Service    → processes the business logic")
        description.append("    Repository → reads/writes to the database")
    elif 'python' in languages:
        description.append("This is a PYTHON APPLICATION.")
        description.append("")
        description.append("  Python powers the logic of this project — whether that's")
        description.append("  a web server, a data pipeline, an automation script, or an AI model.")
    else:
        description.append("This is a SOFTWARE PROJECT with multiple interconnected files.")

    description.append("")
    description.append("=" * 60)

    return "\n".join(description)


def render_multi_language(all_facts, project_name="Project"):
    print("\n" + "="*60)
    print(f"HIRO Analysis: {project_name}")
    print("="*60)

    if not isinstance(all_facts, dict):
        print(f"✗ Error: Expected dict of facts, got {type(all_facts)}")
        return

    cross_deps = detect_cross_language_dependencies(all_facts)
    mermaid_code = build_mermaid_multi_language(all_facts)

    print("=== MERMAID CODE ===")
    print(mermaid_code)
    print()

    description = generate_description(all_facts, cross_deps)
    print("=== DESCRIPTION ===")
    print(description)
    print()

    print("="*60)
    print("Analysis complete.")
    print("="*60)


def render_single_file(facts):
    if not isinstance(facts, dict):
        print(f"✗ Error: Expected facts dict, got {type(facts)}")
        return
    all_facts = {facts['language']: [facts]}
    render_multi_language(all_facts, facts.get('filename', 'unknown'))