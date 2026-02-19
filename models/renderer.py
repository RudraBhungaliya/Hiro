from pathlib import Path


def json_to_mermaid(diagram_data):
    """
    Converts nodes and edges JSON into Mermaid diagram syntax.
    Returns mermaid code as a clean string.
    """
    lines = ["graph TD"]

    for node in diagram_data["nodes"]:
        node_id = node["id"]
        label = node["label"]
        node_type = node["type"]

        if node_type == "class":
            lines.append(f'    {node_id}["{label}"]')
        elif node_type == "method":
            lines.append(f'    {node_id}("{label}")')
        elif node_type == "function":
            lines.append(f'    {node_id}[("{label}")]')

    lines.append("")

    for edge in diagram_data["edges"]:
        from_id = edge["from"]
        to_id = edge["to"]
        label = edge["label"]
        lines.append(f'    {from_id} -->|{label}| {to_id}')

    return "\n".join(lines)


def get_description(diagram_data):
    """Safely extract description from diagram data."""
    return diagram_data.get("description", "")


def render(diagram_data, output_path="diagram.mmd"):
    """
    Master render function.
    Prints and saves Mermaid code and description.
    """
    mermaid_code = json_to_mermaid(diagram_data)
    description = get_description(diagram_data)

    print("=== MERMAID CODE ===")
    print(mermaid_code)
    print()

    if description:
        print("=== DESCRIPTION ===")
        print(description)
        print()

    output = mermaid_code
    if description:
        output += f"\n\n---\n{description}"

    Path(output_path).write_text(output)
    print(f"Saved → {output_path}")

    return mermaid_code, description