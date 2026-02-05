from __future__ import annotations
import subprocess
from pathlib import Path
from typing import List, Optional

class HookSystem:
    def __init__(self, repo_root: str):
        self.repo_root = Path(repo_root).resolve()

    def run_hook(self, hook_name: str, args: List[str] = []) -> Optional[str]:
        """Run a custom hook script if it exists in .vibe/hooks/"""
        hook_path = self.repo_root / ".vibe" / "hooks" / hook_name
        if hook_path.exists():
            try:
                cmd = [str(hook_path)] + args
                res = subprocess.run(cmd, capture_output=True, text=True, check=True)
                return res.stdout
            except Exception as e:
                return f"Hook failed: {str(e)}"
        return None

    def list_hooks(self) -> List[str]:
        hooks_dir = self.repo_root / ".vibe" / "hooks"
        if hooks_dir.exists():
            return [f.name for f in hooks_dir.iterdir() if f.is_file()]
        return []
