from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
import subprocess
from datetime import datetime
from typing import Dict, List, Optional

@dataclass
class GitFileMetric:
    path: str
    commit_count: int
    last_commit_timestamp: str

@dataclass
class GitVelocitySnapshot:
    history_status: str = "stable" # "stable", "high_velocity", "no_history"
    history_note: str = ""
    files: List[GitFileMetric] = field(default_factory=list)

    def by_path(self) -> Dict[str, GitFileMetric]:
        return {f.path: f for f in self.files}

def compute_git_velocity_snapshot(repo_path: Path, days: int = 90) -> GitVelocitySnapshot:
    """Computes commit velocity metrics for files in the repository."""
    snapshot = GitVelocitySnapshot()
    
    try:
        # Get list of files and their commit counts in the last X days
        cmd = [
            "git", "-C", str(repo_path), "log", 
            f"--since={days} days ago", "--name-only", "--pretty=format:"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        
        if result.returncode != 0:
            snapshot.history_status = "no_history"
            snapshot.history_note = "Git log failed or no git repository found."
            return snapshot

        file_counts = {}
        for line in result.stdout.splitlines():
            line = line.strip()
            if line:
                file_counts[line] = file_counts.get(line, 0) + 1
        
        # Get last commit timestamp for each file
        for file_path, count in file_counts.items():
            ts_cmd = ["git", "-C", str(repo_path), "log", "-1", "--format=%ct", "--", file_path]
            ts_result = subprocess.run(ts_cmd, capture_output=True, text=True, check=False)
            timestamp = ""
            if ts_result.returncode == 0:
                raw_ts = ts_result.stdout.strip()
                if raw_ts:
                    timestamp = datetime.fromtimestamp(int(raw_ts)).isoformat()
            
            snapshot.files.append(GitFileMetric(
                path=file_path,
                commit_count=count,
                last_commit_timestamp=timestamp
            ))
            
        if not snapshot.files:
            snapshot.history_status = "no_history"
            snapshot.history_note = f"No activity in the last {days} days."
        elif any(f.commit_count > 10 for f in snapshot.files):
            snapshot.history_status = "high_velocity"
            snapshot.history_note = "Multiple files showing frequent changes."
            
    except Exception as e:
        snapshot.history_status = "no_history"
        snapshot.history_note = f"Error computing git velocity: {str(e)}"
        
    return snapshot
