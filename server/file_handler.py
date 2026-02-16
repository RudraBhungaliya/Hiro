import os

def scan_project(path):
    """
    Scans the given directory path for .js, .py, and .html files.
    Ignores common directories like node_modules, .git, .venv, etc.
    Returns a list of dictionaries containing file data.
    """
    allowed_extensions = {'.js', '.jsx', '.py', '.html', '.css'}
    ignored_dirs = {'node_modules', '.git', '.venv', '__pycache__', 'dist', 'build', '.idea', '.vscode'}
    
    project_files = []
    
    try:
        if not os.path.exists(path):
            return {"error": "Path does not exist"}
        
        for root, dirs, files in os.walk(path):
            # Modify dirs in-place to skip ignored directories
            dirs[:] = [d for d in dirs if d not in ignored_dirs]
            
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in allowed_extensions:
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                        # Store relative path for cleaner output
                        rel_path = os.path.relpath(file_path, path)
                        
                        project_files.append({
                            "name": file,
                            "path": rel_path,
                            "content": content,
                            "type": ext[1:] # remove dot
                        })
                    except Exception as e:
                        print(f"Error reading {file_path}: {e}")
                        # Skip files that can't be read (e.g. binary or encoding issues)
                        continue
                        
        return project_files
        
    except Exception as e:
        return {"error": str(e)}
