"""
Language-specific extractors for HIRO multi-language support.
"""

from models.extractors.py_extractor import extract_python
from models.extractors.java_extractor import extract_java
from models.extractors.js_extractor import extract_javascript
from models.extractors.ts_extractor import extract_typescript
from models.extractors.html_extractor import extract_html
from models.extractors.css_extractor import extract_css

__all__ = [
    'extract_python',
    'extract_java',
    'extract_javascript',
    'extract_typescript',
    'extract_html',
    'extract_css'
]