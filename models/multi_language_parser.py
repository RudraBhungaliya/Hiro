"""
Multi-Language Parser
"""

from pathlib import Path
from models.universe_parser import parse_file_universal, detect_language
from models.extractors.py_extractor import extract_python
from models.extractors.java_extractor import extract_java
from models.extractors.js_extractor import extract_javascript
from models.extractors.ts_extractor import extract_typescript


def parse_file_any_language(filepath):
    filepath = Path(filepath)
    tree, language, code = parse_file_universal(filepath)

    extractors = {
        'python':     extract_python,
        'java':       extract_java,
        'javascript': extract_javascript,
        'typescript': extract_typescript,
        'tsx':        extract_typescript,
    }

    extractor = extractors.get(language)
    if not extractor:
        raise ValueError(f"No extractor for language: {language}")

    facts = extractor(tree, code)
    facts['language'] = language
    facts['filepath'] = str(filepath)
    facts['filename'] = filepath.name

    return facts


def is_backend_file(filepath):
    """
    Returns True only for files that are actual backend logic.
    Filters out tests, config, minified, and frontend files.
    """
    path = Path(filepath)
    name = path.name.lower()
    parts = [p.lower() for p in path.parts]

    # Skip test files
    if any(p in parts for p in ['test', 'tests', '__tests__', 'spec', 'specs']):
        return False
    if name.endswith('.test.js') or name.endswith('.spec.js'):
        return False
    if name.endswith('.test.ts') or name.endswith('.spec.ts'):
        return False

    # Skip minified files
    if '.min.' in name:
        return False

    # Skip config / setup / seed files
    skip_names = [
        'config.js', 'setup.js', 'seed.js', 'jest.config.js',
        'webpack.config.js', 'babel.config.js', 'rollup.config.js',
        'vite.config.js', 'tailwind.config.js', 'postcss.config.js',
        '.eslintrc.js', 'prettier.config.js'
    ]
    if name in skip_names:
        return False

    # Skip node_modules, build output, etc.
    excluded_dirs = [
        'node_modules', 'venv', '__pycache__', 'build',
        'dist', '.git', 'target', 'out', '.next', '.nuxt',
        'coverage', 'public', 'static', 'assets'
    ]
    if any(ex in parts for ex in excluded_dirs):
        return False

    return True


def parse_folder_multi_language(folder_path):
    folder = Path(folder_path)

    # Only backend-relevant extensions — no HTML, CSS
    supported_extensions = ['.py', '.java', '.js', '.jsx', '.ts', '.tsx']
    all_files = []

    for ext in supported_extensions:
        all_files.extend(folder.rglob(f'*{ext}'))

    # Apply backend filter
    filtered_files = [f for f in all_files if is_backend_file(f)]

    print(f"Found {len(filtered_files)} backend files "
          f"(filtered from {len(all_files)} total)")

    # Group by language
    files_by_language = {}
    for file in filtered_files:
        lang = detect_language(file)
        if lang not in files_by_language:
            files_by_language[lang] = []
        files_by_language[lang].append(file)

    # Parse each file
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