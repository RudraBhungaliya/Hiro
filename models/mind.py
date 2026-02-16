import sys
from models.folder_parser import parse_folder
from models.parser import parse_file
from models.renderer import json_to_mermaid
def main():
    if len(sys.argv) < 3:
        print("Usage:")
        print("  python devmind.py --file yourfile.py")
        print("  python devmind.py --folder ./your-project")
        sys.exit(1)

    mode = sys.argv[1]
    target = sys.argv[2]

    if mode == "--file":
        print(f"HIRO analyzing file: {target}")
        print()
        diagram_data = parse_file(target)

    elif mode == "--folder":
        print(f"HIRO analyzing folder: {target}")
        print()
        diagram_data = parse_folder(target)

    else:
        print(f"Unknown mode: {mode}")
        sys.exit(1)

    mermaid_code = json_to_mermaid(diagram_data)

    print()
    print("=== MERMAID CODE ===")
    print(mermaid_code)


if __name__ == "__main__":
    main()