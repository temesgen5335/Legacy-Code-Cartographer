from pathlib import Path

repo_path = Path("targets/networkx_networkx.git")
print(f"Checking path: {repo_path.absolute()}")

extensions = [".py", ".sql"]
files_to_analyze = []
for ext in extensions:
    files = list(repo_path.rglob(f"*{ext}"))
    print(f"Found {len(files)} files with extension {ext}")
    files_to_analyze.extend(files)

for i, file_path in enumerate(files_to_analyze[:10]):
    parts = file_path.parts
    skip = any(p in ["venv", ".git", ".cartography"] for p in parts)
    print(f"File: {file_path}, Parts: {parts}, Skip: {skip}")

total_analyzed = sum(1 for f in files_to_analyze if not any(p in ["venv", ".git", ".cartography"] for p in f.parts))
print(f"Total files that would be analyzed: {total_analyzed}")
