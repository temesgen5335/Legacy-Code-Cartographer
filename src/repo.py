from pathlib import Path

def repository_metadata(repo_input: str, repo_path: Path) -> dict:
    """Extracts basic repository metadata from the path or input string."""
    try:
        # Simple local-first strategy
        return {
            "owner": "local",
            "repo_name": repo_path.name,
            "branch": "main",
            "display_name": repo_path.name,
            "repo_url": str(repo_input),
        }
    except Exception:
        return {
            "owner": "unknown",
            "repo_name": "unknown",
            "branch": "unknown",
            "display_name": "unknown",
            "repo_url": str(repo_input),
        }
