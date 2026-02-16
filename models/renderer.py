def json_to_mermaid(diagram_data):
    """
    Converts nodes and edges JSON into Mermaid diagram syntax.
    Returns mermaid code + description as one clean string.
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

    # Append description below the diagram
    if "description" in diagram_data and diagram_data["description"]:
        lines.append("")
        lines.append("")
        lines.append("%% ─────────────────────────────────────────")
        lines.append("%% HIRO Analysis")
        lines.append("%% ─────────────────────────────────────────")
        for line in diagram_data["description"].split("\n"):
            lines.append(f"%% {line}")

    return "\n".join(lines)