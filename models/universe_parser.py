"""
Universal Parser using Tree-sitter
Provides a consistent interface for parsing any supported language.
"""

from tree_sitter import Language, Parser
import tree_sitter_python as ts_python
import tree_sitter_java as ts_java
import tree_sitter_javascript as ts_javascript
import tree_sitter_typescript as ts_typescript
import tree_sitter_html as ts_html
import tree_sitter_css as ts_css
from pathlib import Path


# Initialize language objects using the new API
PY_LANGUAGE = Language(ts_python.language())
JAVA_LANGUAGE = Language(ts_java.language())
JS_LANGUAGE = Language(ts_javascript.language())
TS_LANGUAGE = Language(ts_typescript.language_typescript())
TSX_LANGUAGE = Language(ts_typescript.language_tsx())
HTML_LANGUAGE = Language(ts_html.language())
CSS_LANGUAGE = Language(ts_css.language())

LANGUAGES = {
    'python': PY_LANGUAGE,
    'java': JAVA_LANGUAGE,
    'javascript': JS_LANGUAGE,
    'typescript': TS_LANGUAGE,
    'tsx': TSX_LANGUAGE,
    'html': HTML_LANGUAGE,
    'css': CSS_LANGUAGE
}


def detect_language(filepath):
    """
    Detect language from file extension.
    
    Returns: language string for tree-sitter
    """
    extension_map = {
        '.py': 'python',
        '.java': 'java',
        '.js': 'javascript',
        '.jsx': 'javascript',
        '.ts': 'typescript',
        '.tsx': 'tsx',
        '.html': 'html',
        '.htm': 'html',
        '.css': 'css',
        '.scss': 'css'
    }
    
    ext = Path(filepath).suffix.lower()
    return extension_map.get(ext, 'unknown')


def parse_file_universal(filepath):
    """
    Universal parser that works for ANY supported language.
    
    Returns: (tree, language, code_bytes)
    """
    # Detect language
    language = detect_language(filepath)
    
    if language == 'unknown':
        raise ValueError(f"Unsupported file type: {filepath}")
    
    # Read file as bytes (tree-sitter requires bytes)
    with open(filepath, 'rb') as f:
        code = f.read()
    
    # Get the language object
    lang_obj = LANGUAGES[language]
    
    # Create parser with the new API
    parser = Parser(lang_obj)
    
    # Parse code
    tree = parser.parse(code)
    
    return tree, language, code


def get_node_text(node, code):
    """Extract text from a tree-sitter node."""
    return code[node.start_byte:node.end_byte].decode('utf-8', errors='ignore')