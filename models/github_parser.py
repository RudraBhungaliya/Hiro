import tempfile
import shutil
from pathlib import Path
from git import Repo
from models.folder_parser import parse_folder


def parse_github_repo(repo_url):
    """
    Clones a GitHub repository, analyzes it, and returns diagram data.
    Automatically cleans up after itself.
    
    Args:
        repo_url: GitHub repository URL (https://github.com/user/repo)
    
    Returns:
        dict with nodes, edges, description
    """
    temp_dir = None
    
    try:
        temp_dir = tempfile.mkdtemp(prefix="hiro_clone_")
        print(f"Cloning {repo_url}...")
        
        Repo.clone_from(repo_url, temp_dir, depth=1)
        print(f"Cloned to {temp_dir}")
        print()
        
        diagram_data = parse_folder(temp_dir)
        
        return diagram_data
        
    except Exception as e:
        raise Exception(f"Failed to analyze repository: {str(e)}")
        
    finally:
        if temp_dir and Path(temp_dir).exists():
            shutil.rmtree(temp_dir)
            print(f"Cleaned up temporary files")


def validate_github_url(url):
    """Validates that the URL is a proper GitHub repository URL."""
    if not url.startswith(("https://github.com/", "http://github.com/")):
        return False
    
    parts = url.replace("https://", "").replace("http://", "").split("/")
    if len(parts) < 3:
        return False
    
    return True