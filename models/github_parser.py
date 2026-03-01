import tempfile
import shutil
from pathlib import Path
from git import Repo

from models.multi_language_parser import parse_folder_multi_language
def parse_github_repo(repo_url):
    temp_dir = None
    try:
        temp_dir = tempfile.mkdtemp(prefix="hiro_clone_")
        print(f"Cloning {repo_url}...")
        
        Repo.clone_from(repo_url, temp_dir, depth=1)
        print(f"Cloned to {temp_dir}")
        print()
        all_facts = parse_folder_multi_language(temp_dir)
        return all_facts

        
    except Exception as e:
        raise Exception(f"Failed to analyze repository: {str(e)}")
        
    finally:
        if temp_dir and Path(temp_dir).exists():
            shutil.rmtree(temp_dir)
            print(f"Cleaned up temporary files")


def validate_github_url(url):
    if not url.startswith(("https://github.com/", "http://github.com/")):
        return False
    parts = url.replace("https://", "").replace("http://", "").split("/")
    if len(parts) < 3:
        return False
    return True