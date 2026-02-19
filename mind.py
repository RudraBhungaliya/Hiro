import sys
from models.parser import parse_file
from models.folder_parser import parse_folder
from models.github_parser import parse_github_repo, validate_github_url
from models.renderer import render


def main():
    if len(sys.argv) < 3:
        print("Usage:")
        print("  python devmind.py --file yourfile.py")
        print("  python devmind.py --folder ./your-project")
        print("  python devmind.py --github https://github.com/user/repo")
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

    elif mode == "--github":
        if not validate_github_url(target):
            print("Invalid GitHub URL. Use format: https://github.com/user/repo")
            sys.exit(1)
        
        print(f"HIRO analyzing GitHub repository: {target}")
        print()
        diagram_data = parse_github_repo(target)

    else:
        print(f"Unknown mode: {mode}")
        sys.exit(1)

    render(diagram_data)
    print()
    print("Done.")


if __name__ == "__main__":
    main()