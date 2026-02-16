import ast
import os

def analyze_directory(directory_path):
    """
    Analyzes a directory of Python files and generates a Mermaid class diagram.
    """
    classes = []
    relationships = []

    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        tree = ast.parse(f.read(), filename=file_path)
                        analyze_ast(tree, classes, relationships)
                except Exception as e:
                    print(f"Skipping {file}: {e}")

    return generate_mermaid(classes, relationships)

def analyze_ast(tree, classes, relationships):
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            class_name = node.name
            classes.append(class_name)
            for base in node.bases:
                if isinstance(base, ast.Name):
                    relationships.append((base.id, class_name))
                elif isinstance(base, ast.Attribute):
                     # Handle module.Class
                    relationships.append((base.attr, class_name))

def generate_mermaid(classes, relationships):
    lines = ["classDiagram"]
    
    # Add classes
    for cls in classes:
        lines.append(f"    class {cls}")
    
    # Add relationships (Inheritance)
    for parent, child in relationships:
        # Only add relationship if parent is also a known class or explicitly desired
        # For simplicity, we just add it.
        lines.append(f"    {parent} <|-- {child}")
        
    return "\n".join(lines)
