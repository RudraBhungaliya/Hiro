"""
HIRO - Multi-Language Architecture Analyzer
Supports: Python, Java, JavaScript, React, TypeScript, HTML, CSS
"""

import sys
from pathlib import Path


def main():
    if len(sys.argv) < 2:
        print("HIRO - Multi-Language Architecture Analyzer")
        print()
        print("Usage:")
        print("  python mind.py --file <filepath>")
        print("  python mind.py --folder <folder_path>")
        print("  python mind.py --github <github_url>")
        print("  python mind.py --clear-cache")
        print("  python mind.py --cache-info")
        print()
        print("Supported Languages:")
        print("  • Python (.py)")
        print("  • Java (.java) - Spring Boot")
        print("  • JavaScript (.js, .jsx) - React")
        print("  • TypeScript (.ts, .tsx)")
        print("  • HTML (.html)")
        print("  • CSS (.css)")
        print()
        print("Examples:")
        print("  python mind.py --file app.py")
        print("  python mind.py --folder ./my-project")
        print("  python mind.py --github https://github.com/user/repo")
        sys.exit(1)

    mode = sys.argv[1]

    # ── Cache management commands (no target needed) ──────────
    if mode == "--clear-cache":
        from models.diagram_cache import clear_cache
        clear_cache()
        sys.exit(0)

    if mode == "--cache-info":
        from models.diagram_cache import cache_info
        cache_info()
        sys.exit(0)
    # ─────────────────────────────────────────────────────────

    if len(sys.argv) < 3:
        print(f"✗ Missing target for {mode}")
        print("Run 'python mind.py' for help")
        sys.exit(1)

    target = sys.argv[2]

    if mode == "--file":
        print(f"🔍 HIRO analyzing file: {target}")
        print()

        from models.multi_language_parser import parse_file_any_language
        from models.multi_language_renderer import render_single_file

        try:
            facts = parse_file_any_language(target)
            render_single_file(facts)
            print("✓ Analysis complete")
        except Exception as e:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

    elif mode == "--folder":
        print(f"🔍 HIRO analyzing folder: {target}")
        print()

        from models.multi_language_parser import parse_folder_multi_language
        from models.ai_engine import analyze_with_gemini
        from models.multi_language_renderer import render_ai_diagram

        try:
            all_facts = parse_folder_multi_language(target)

            print("=== DEBUG: FILES FOUND ===")
            for lang, facts_list in all_facts.items():
                print(f"{lang}: {len(facts_list)} files")
            print("==========================")
            print()

            print("🤖 Running AI architecture analysis...")
            result = analyze_with_gemini(all_facts)
            render_ai_diagram(result)
            print("✓ Analysis complete")
        except Exception as e:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

    elif mode == "--github":
        print(f"🔍 HIRO analyzing GitHub repository: {target}")
        print()

        try:
            from models.github_parser import parse_github_repo, validate_github_url
        except ImportError as e:
            print("✗ GitHub integration not available.")
            print()
            if "git" in str(e).lower():
                print("Git is not installed on your system.")
                print()
                print("To enable GitHub integration, install Git:")
                print("  macOS:   xcode-select --install")
                print("  Linux:   sudo apt-get install git")
                print("  Windows: Download from https://git-scm.com/")
                print()
                print("After installing git, run:")
                print("  pip install gitpython")
            else:
                print("GitPython is not installed.")
                print()
                print("Install it with:")
                print("  pip install gitpython")
            print()
            print("💡 You can still analyze local files and folders:")
            print("  python mind.py --file <filepath>")
            print("  python mind.py --folder <folder_path>")
            sys.exit(1)

        from models.ai_engine import analyze_with_gemini
        from models.multi_language_renderer import render_ai_diagram

        if not validate_github_url(target):
            print("✗ Invalid GitHub URL. Use format: https://github.com/user/repo")
            sys.exit(1)

        try:
            all_facts = parse_github_repo(target)

            print("=== DEBUG: FILES FOUND ===")
            for lang, facts_list in all_facts.items():
                print(f"{lang}: {len(facts_list)} files")
            print("==========================")
            print()

            print("🤖 Running AI architecture analysis...")
            result = analyze_with_gemini(all_facts)
            render_ai_diagram(result)
            print("✓ Analysis complete")
        except Exception as e:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

    else:
        print(f"✗ Unknown mode: {mode}")
        print()
        print("Valid modes: --file, --folder, --github")
        print("Run 'python mind.py' for help")
        sys.exit(1)


if __name__ == "__main__":
    main()
