"""
Multi-Language Renderer
Renders the structured output from ai_engine.py into Mermaid + description.
"""

from pathlib import Path
from models.ai_engine import analyze_with_gemini


# Mermaid shape per role
ROLE_SHAPES = {
    'client':     lambda label: f'(["{label}"])',
    'entry':      lambda label: f'["{label}"]',
    'middleware': lambda label: f'{{"{label}"}}',
    'router':     lambda label: f'["{label}"]',
    'controller': lambda label: f'["{label}"]',
    'service':    lambda label: f'("{label}")',
    'repository': lambda label: f'[/"{label}"/]',
    'database':   lambda label: f'[("{label}")]',
    'entity':     lambda label: f'[/"{label}"/]',
    'utility':    lambda label: f'("{label}")',
    'component':  lambda label: f'(("{label}"))',
    'external':   lambda label: f'(("{label}"))',
    'module':     lambda label: f'["{label}"]',
}

ROLE_ICONS = {
    'client':     '🌐',
    'entry':      '🚀',
    'router':     '🔀',
    'controller': '🎮',
    'service':    '⚙️',
    'repository': '🗄️',
    'database':   '💾',
    'middleware': '🔒',
    'entity':     '📦',
    'utility':    '🔧',
    'component':  '⚛️',
    'external':   '📡',
    'module':     '📄',
}

ROLE_ORDER = [
    'client',
    'entry',
    'middleware',
    'router',
    'controller',
    'service',
    'repository',
    'entity',
    'database',
    'external',
    'utility',
    'component',
    'module'
]


def build_mermaid_from_ai(ai_result):
    """
    Converts AI engine output into Mermaid diagram code.
    """
    nodes = ai_result.get("diagram", {}).get("nodes", [])
    edges = ai_result.get("diagram", {}).get("edges", [])

    lines = ["graph TD"]
    lines.append("")

    # Group nodes by role
    role_groups = {}
    for node in nodes:
        role = node.get("role", "module")
        if role not in role_groups:
            role_groups[role] = []
        role_groups[role].append(node)

    # Render nodes grouped by role in architectural order
    for role in ROLE_ORDER:
        if role not in role_groups:
            continue

        group_nodes = role_groups[role]
        role_label  = role.upper().replace("_", " ")
        lines.append(f"    %% ── {role_label} ──")

        for node in group_nodes:
            node_id    = node.get("id", "unknown")
            label      = node.get("label", "unknown")
            icon       = ROLE_ICONS.get(role, "📄")
            full_label = f"{icon} {label}"

            shape_fn = ROLE_SHAPES.get(role, ROLE_SHAPES['module'])
            shape    = shape_fn(full_label)

            lines.append(f"    {node_id}{shape}")

        lines.append("")

    # Render edges
    if edges:
        lines.append("    %% ── DATA FLOW ──")
        for edge in edges:
            from_id    = edge.get("from")
            to_id      = edge.get("to")
            edge_label = edge.get("label", "")
            if from_id and to_id:
                lines.append(f"    {from_id} -->|{edge_label}| {to_id}")

    return "\n".join(lines)


def build_description_from_ai(ai_result):
    """
    Converts AI engine output into plain English description.
    3 sections only: Overview, Components, Architecture Pattern.
    """
    desc_data    = ai_result.get("description", {})
    project_name = ai_result.get("project_name", "Software Project")
    overview     = desc_data.get("overview", "")
    components   = desc_data.get("components", [])
    architecture = desc_data.get("architecture_pattern", "")

    lines = []

    # ── HEADER ────────────────────────────────────────────────
    lines.append("=" * 60)
    lines.append(f"  {project_name}")
    lines.append("=" * 60)
    lines.append("")

    # ── OVERVIEW ──────────────────────────────────────────────
    lines.append("OVERVIEW")
    lines.append("─" * 40)
    lines.append(overview)
    lines.append("")

    # ── COMPONENTS ────────────────────────────────────────────
    lines.append("COMPONENTS")
    lines.append("─" * 40)

    role_icons = {
        'Controller':   '🎮',
        'Service':      '⚙️',
        'Repository':   '🗄️',
        'Entity':       '📦',
        'Router':       '🔀',
        'Database':     '💾',
        'Middleware':   '🔒',
        'Utility':      '🔧',
        'Entry Point':  '🚀',
        'External':     '📡',
        'Client':       '🌐',
        'Module':       '📄',
    }

    for comp in components:
        name         = comp.get("name", "")
        role         = comp.get("role", "Module")
        what_it_does = comp.get("what_it_does", "")
        icon         = role_icons.get(role, "📄")

        lines.append(f"  {icon} {name}")
        lines.append(f"     [{role}]")
        lines.append(f"     {what_it_does}")
        lines.append("")

    # ── ARCHITECTURE PATTERN ──────────────────────────────────
    lines.append("ARCHITECTURE PATTERN")
    lines.append("─" * 40)
    lines.append(architecture)
    lines.append("")
    lines.append("=" * 60)

    return "\n".join(lines)


def render_multi_language(all_facts, project_name="Project"):
    """
    Master render function.
    Calls AI engine then renders diagram + description.
    """
    print("\n" + "=" * 60)
    print(f"HIRO Analysis: {project_name}")
    print("=" * 60)

    if not isinstance(all_facts, dict):
        print(f"✗ Error: Expected dict, got {type(all_facts)}")
        return

    try:
        ai_result = analyze_with_gemini(all_facts)
    except Exception as e:
        print(f"✗ AI Engine error: {e}")
        return

    mermaid_code = build_mermaid_from_ai(ai_result)
    description  = build_description_from_ai(ai_result)

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


def has_renderable_content(facts):
    if not isinstance(facts, dict):
        return False
    return any([
        facts.get('classes'),
        facts.get('components'),
        facts.get('functions'),
        facts.get('spring_patterns', {}).get('controllers'),
    ])