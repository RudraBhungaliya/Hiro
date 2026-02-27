"""
Multi-Language Parser
Unified interface for analyzing projects with multiple languages.
"""

from pathlib import Path
from models.universe_parser import parse_file_universal, detect_language
from models.extractors.py_extractor import extract_python
from models.extractors.java_extractor import extract_java
from models.extractors.js_extractor import extract_javascript
from models.extractors.ts_extractor import extract_typescript
from models.extractors.html_extractor import extract_html
from models.extractors.css_extractor import extract_css


def parse_file_any_language(filepath):
    """
    Universal parser that automatically detects language
    and extracts appropriate structure.
    
    Args:
        filepath: Path to source file (string or Path object)
    
    Returns:
        Unified facts dictionary
    """
    
    # Convert to Path object if string
    filepath = Path(filepath)
    
    # Parse with tree-sitter
    tree, language, code = parse_file_universal(filepath)
    
    # Route to appropriate extractor
    extractors = {
        'python': extract_python,
        'java': extract_java,
        'javascript': extract_javascript,
        'typescript': extract_typescript,
        'tsx': extract_typescript,
        'html': extract_html,
        'css': extract_css
    }
    
    extractor = extractors.get(language)
    if not extractor:
        raise ValueError(f"No extractor for language: {language}")
    
    # Extract facts
    facts = extractor(tree, code)
    
    # Add metadata
    facts['language'] = language
    facts['filepath'] = str(filepath)
    facts['filename'] = filepath.name
    
    return facts


def parse_folder_multi_language(folder_path):
    """
    Parse entire project with multiple languages.
    
    Handles:
    - Python backend
    - Java Spring Boot
    - React frontend
    - HTML/CSS
    - Mixed projects (full-stack)
    
    Returns:
        Dictionary with facts organized by language
    """
    
    folder = Path(folder_path)
    
    # Find all supported files
    supported_extensions = ['.py', '.java', '.js', '.jsx', '.ts', '.tsx', '.html', '.css']
    all_files = []
    
    for ext in supported_extensions:
        all_files.extend(folder.rglob(f'*{ext}'))
    
    # Filter out build/dependency folders
    filtered_files = [
        f for f in all_files
        if not any(excluded in str(f) for excluded in [
            'node_modules', 'venv', '__pycache__', 'build', 'dist',
            '.git', 'target', 'out', '.next', '.nuxt'
        ])
    ]
    
    print(f"Found {len(filtered_files)} files across {len(set(f.suffix for f in filtered_files))} languages")
    
    # Group by language
    files_by_language = {}
    for file in filtered_files:
        lang = detect_language(file)
        if lang not in files_by_language:
            files_by_language[lang] = []
        files_by_language[lang].append(file)
    
    # Parse each language group
    all_facts = {}
    for language, files in files_by_language.items():
        print(f"\nAnalyzing {len(files)} {language} files...")
        language_facts = []
        
        for file in files:
            try:
                facts = parse_file_any_language(file)
                language_facts.append(facts)
                print(f"  ✓ {file.name}")
            except Exception as e:
                print(f"  ✗ {file.name}: {e}")
                continue
        
        all_facts[language] = language_facts
    
    return all_facts


def build_unified_graph(all_facts):
    """
    Build unified architecture graph from multi-language facts.
    
    Args:
        all_facts: Dictionary of facts by language
    
    Returns:
        Unified graph with nodes and edges
    """
    
    nodes = []
    edges = []
    id_counter = 1
    
    # Build nodes for each language
    for language, facts_list in all_facts.items():
        for facts in facts_list:
            # Add classes
            for cls in facts.get('classes', []):
                # Skip if classes is a list of strings (CSS classes)
                if isinstance(cls, str):
                    continue
                    
                node_id = str(id_counter)
                id_counter += 1
                
                nodes.append({
                    'id': node_id,
                    'label': cls['name'],
                    'type': f'{language}_class',
                    'language': language,
                    'file': facts['filename']
                })
                
                # Add methods as child nodes
                for method in cls.get('methods', []):
                    method_id = str(id_counter)
                    id_counter += 1
                    
                    nodes.append({
                        'id': method_id,
                        'label': method,
                        'type': 'method',
                        'language': language,
                        'parent': node_id
                    })
                    
                    edges.append({
                        'from': node_id,
                        'to': method_id,
                        'label': 'has method'
                    })
            
            # Add components (React)
            for comp in facts.get('components', []):
                node_id = str(id_counter)
                id_counter += 1
                
                nodes.append({
                    'id': node_id,
                    'label': comp['name'],
                    'type': 'react_component',
                    'language': language,
                    'file': facts['filename']
                })
    
    return {
        'nodes': nodes,
        'edges': edges,
        'languages': list(all_facts.keys()),
        'file_count': sum(len(facts_list) for facts_list in all_facts.values())
    }