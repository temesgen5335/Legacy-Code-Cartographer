import os
from pathlib import Path
from typing import Dict, List, Set

class LanguageRouter:
    """
    Identifies the primary and secondary languages and frameworks in a codebase.
    """
    
    ANCHOR_FILES = {
        "pyproject.toml": "python",
        "requirements.txt": "python",
        "setup.py": "python",
        "dbt_project.yml": "dbt",
        "pom.xml": "java",
        "build.gradle": "java",
        "package.json": "javascript",
        "docker-compose.yml": "docker",
        "Dockerfile": "docker",
        "Jenkinsfile": "jenkins",
        "dag.py": "airflow",  # Heuristic for airflow
    }
    
    EXTENSIONS = {
        ".py": "python",
        ".sql": "sql",
        ".yaml": "yaml",
        ".yml": "yaml",
        ".java": "java",
        ".js": "javascript",
        ".ts": "typescript",
        ".ipynb": "jupyter",
        ".scala": "scala",
    }

    def __init__(self, root_path: str):
        self.root_path = Path(root_path)
        self.languages: Set[str] = set()
        self.frameworks: Set[str] = set()

    def detect(self) -> Dict[str, List[str]]:
        """
        Scans the file tree to identify languages and frameworks.
        """
        for path in self.root_path.rglob("*"):
            if path.is_file():
                # Check for anchor files
                if path.name in self.ANCHOR_FILES:
                    framework = self.ANCHOR_FILES[path.name]
                    self.frameworks.add(framework)
                
                # Check for extensions
                ext = path.suffix
                if ext in self.EXTENSIONS:
                    self.languages.add(self.EXTENSIONS[ext])
        
        return {
            "languages": sorted(list(self.languages)),
            "frameworks": sorted(list(self.frameworks))
        }

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        router = LanguageRouter(sys.argv[1])
        print(router.detect())
    else:
        print("Usage: python language_router.py <path>")
