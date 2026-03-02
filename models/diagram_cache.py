"""
HIRO Diagram Cache
Stores AI-generated architecture results keyed by a hash of the codebase facts.
Ensures the same codebase always produces the same diagram.
"""

import json
import hashlib
import os
from pathlib import Path

# Cache lives next to this file, in a .hiro_cache directory
CACHE_DIR = Path(os.getenv("HIRO_CACHE_DIR", Path.home() / ".hiro_cache"))


def _ensure_cache_dir():
    CACHE_DIR.mkdir(parents=True, exist_ok=True)


def _compute_hash(all_facts: dict) -> str:
    """
    Deterministic hash of the codebase facts.
    Sorts keys so dict ordering doesn't affect the hash.
    """
    canonical = json.dumps(all_facts, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _cache_path(facts_hash: str) -> Path:
    return CACHE_DIR / f"{facts_hash}.json"


def get_cached(all_facts: dict):
    """
    Returns the cached AI result for this codebase, or None if not cached.
    """
    facts_hash = _compute_hash(all_facts)
    path = _cache_path(facts_hash)

    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                cached = json.load(f)
            print(f"✓ Cache hit — loading saved diagram (hash: {facts_hash[:12]}...)")
            return cached
        except (json.JSONDecodeError, OSError) as e:
            print(f"⚠ Cache read error ({e}), regenerating...")
            return None

    return None


def save_to_cache(all_facts: dict, result: dict):
    """
    Saves an AI result to disk, keyed by codebase hash.
    """
    _ensure_cache_dir()
    facts_hash = _compute_hash(all_facts)
    path = _cache_path(facts_hash)

    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"✓ Diagram cached (hash: {facts_hash[:12]}...)")
    except OSError as e:
        print(f"⚠ Cache write error: {e} — continuing without caching")


def clear_cache():
    """
    Deletes all cached diagrams. Useful for forcing a fresh analysis.
    """
    _ensure_cache_dir()
    deleted = 0
    for f in CACHE_DIR.glob("*.json"):
        f.unlink()
        deleted += 1
    print(f"✓ Cleared {deleted} cached diagram(s) from {CACHE_DIR}")


def cache_info():
    """
    Prints info about what's currently cached.
    """
    _ensure_cache_dir()
    entries = list(CACHE_DIR.glob("*.json"))
    print(f"Cache directory: {CACHE_DIR}")
    print(f"Cached diagrams: {len(entries)}")
    for e in entries:
        size_kb = e.stat().st_size / 1024
        print(f"  • {e.stem[:16]}... ({size_kb:.1f} KB)")