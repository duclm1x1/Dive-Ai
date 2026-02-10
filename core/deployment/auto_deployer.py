"""
🚀 AUTO CODE DEPLOY
Automated Git integration for committing and pushing agent changes
"""

import os
import sys
import json
import subprocess
import threading
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))


@dataclass
class GitConfig:
    """Git configuration"""
    repo_path: str
    branch: str = "main"
    remote: str = "origin"
    auto_commit: bool = True
    auto_push: bool = False  # Requires explicit enable
    commit_prefix: str = "[DiveAI]"
    author_name: str = "Dive AI Agent"
    author_email: str = "dive-ai@localhost"


@dataclass
class CommitResult:
    """Result of commit operation"""
    success: bool
    commit_hash: Optional[str] = None
    message: str = ""
    files_changed: int = 0
    insertions: int = 0
    deletions: int = 0
    error: Optional[str] = None


@dataclass
class PullRequestInfo:
    """Pull request information"""
    title: str
    body: str
    branch: str
    base_branch: str = "main"
    files_changed: List[str] = None


class AutoDeployer:
    """
    🚀 Automated Code Deployment System
    - Git integration
    - Auto-commit changes
    - Push to GitHub
    - PR automation
    - Rollback capability
    """
    
    def __init__(self, config: GitConfig):
        self.config = config
        self.lock = threading.Lock()
        self.commit_history: List[CommitResult] = []
        
        # Verify git repo
        self._verify_repo()
    
    def _verify_repo(self):
        """Verify git repository exists"""
        git_dir = Path(self.config.repo_path) / ".git"
        if not git_dir.exists():
            raise ValueError(f"Not a git repository: {self.config.repo_path}")
        print(f"✅ AutoDeployer initialized: {self.config.repo_path}")
    
    def _run_git(self, *args, capture_output: bool = True) -> subprocess.CompletedProcess:
        """Run git command"""
        cmd = ["git"] + list(args)
        return subprocess.run(
            cmd,
            cwd=self.config.repo_path,
            capture_output=capture_output,
            text=True,
            env={
                **os.environ,
                "GIT_AUTHOR_NAME": self.config.author_name,
                "GIT_AUTHOR_EMAIL": self.config.author_email,
                "GIT_COMMITTER_NAME": self.config.author_name,
                "GIT_COMMITTER_EMAIL": self.config.author_email
            }
        )
    
    def get_status(self) -> Dict[str, Any]:
        """Get git status"""
        result = self._run_git("status", "--porcelain")
        
        if result.returncode != 0:
            return {"error": result.stderr}
        
        lines = result.stdout.strip().split("\n") if result.stdout.strip() else []
        
        modified = []
        added = []
        deleted = []
        untracked = []
        
        for line in lines:
            if not line:
                continue
            status = line[:2]
            file_path = line[3:]
            
            if "M" in status:
                modified.append(file_path)
            elif "A" in status:
                added.append(file_path)
            elif "D" in status:
                deleted.append(file_path)
            elif "?" in status:
                untracked.append(file_path)
        
        return {
            "modified": modified,
            "added": added,
            "deleted": deleted,
            "untracked": untracked,
            "total_changes": len(modified) + len(added) + len(deleted),
            "clean": len(lines) == 0
        }
    
    def get_current_branch(self) -> str:
        """Get current branch name"""
        result = self._run_git("rev-parse", "--abbrev-ref", "HEAD")
        return result.stdout.strip() if result.returncode == 0 else "unknown"
    
    def get_last_commit(self) -> Dict[str, str]:
        """Get last commit info"""
        result = self._run_git("log", "-1", "--format=%H|%s|%an|%ar")
        if result.returncode != 0:
            return {"error": result.stderr}
        
        parts = result.stdout.strip().split("|")
        if len(parts) >= 4:
            return {
                "hash": parts[0][:7],
                "message": parts[1],
                "author": parts[2],
                "time": parts[3]
            }
        return {}
    
    def stage_files(self, files: List[str] = None, all_files: bool = False) -> bool:
        """Stage files for commit"""
        with self.lock:
            if all_files:
                result = self._run_git("add", "-A")
            elif files:
                result = self._run_git("add", *files)
            else:
                return False
            
            return result.returncode == 0
    
    def commit(self, message: str, files: List[str] = None, 
               stage_all: bool = True) -> CommitResult:
        """Create commit"""
        with self.lock:
            # Stage files
            if stage_all:
                self.stage_files(all_files=True)
            elif files:
                self.stage_files(files=files)
            
            # Check if there are changes to commit
            status = self.get_status()
            if status.get("clean", True):
                return CommitResult(
                    success=False,
                    message="No changes to commit"
                )
            
            # Create commit
            full_message = f"{self.config.commit_prefix} {message}"
            result = self._run_git("commit", "-m", full_message)
            
            if result.returncode != 0:
                return CommitResult(
                    success=False,
                    error=result.stderr
                )
            
            # Get commit hash
            hash_result = self._run_git("rev-parse", "HEAD")
            commit_hash = hash_result.stdout.strip()[:7] if hash_result.returncode == 0 else None
            
            # Get stats
            stats_result = self._run_git("diff", "--stat", "HEAD~1", "HEAD")
            
            commit_result = CommitResult(
                success=True,
                commit_hash=commit_hash,
                message=full_message,
                files_changed=len(status.get("modified", [])) + len(status.get("added", []))
            )
            
            self.commit_history.append(commit_result)
            
            # Auto-push if enabled
            if self.config.auto_push:
                self.push()
            
            return commit_result
    
    def push(self, force: bool = False) -> bool:
        """Push to remote"""
        with self.lock:
            args = ["push", self.config.remote, self.config.branch]
            if force:
                args.insert(1, "-f")
            
            result = self._run_git(*args)
            return result.returncode == 0
    
    def pull(self, rebase: bool = False) -> bool:
        """Pull from remote"""
        with self.lock:
            args = ["pull", self.config.remote, self.config.branch]
            if rebase:
                args.insert(1, "--rebase")
            
            result = self._run_git(*args)
            return result.returncode == 0
    
    def create_branch(self, branch_name: str, checkout: bool = True) -> bool:
        """Create new branch"""
        with self.lock:
            result = self._run_git("checkout", "-b", branch_name)
            return result.returncode == 0
    
    def checkout(self, branch: str) -> bool:
        """Checkout branch"""
        with self.lock:
            result = self._run_git("checkout", branch)
            return result.returncode == 0
    
    def rollback(self, commit_hash: str = None, soft: bool = True) -> bool:
        """Rollback to previous commit"""
        with self.lock:
            if commit_hash:
                target = commit_hash
            else:
                target = "HEAD~1"
            
            reset_type = "--soft" if soft else "--hard"
            result = self._run_git("reset", reset_type, target)
            return result.returncode == 0
    
    def stash(self, message: str = None) -> bool:
        """Stash changes"""
        with self.lock:
            if message:
                result = self._run_git("stash", "push", "-m", message)
            else:
                result = self._run_git("stash")
            return result.returncode == 0
    
    def stash_pop(self) -> bool:
        """Pop stashed changes"""
        with self.lock:
            result = self._run_git("stash", "pop")
            return result.returncode == 0
    
    def get_diff(self, staged: bool = False) -> str:
        """Get diff of changes"""
        args = ["diff"]
        if staged:
            args.append("--staged")
        
        result = self._run_git(*args)
        return result.stdout if result.returncode == 0 else ""
    
    def prepare_pr_info(self, title: str, description: str = None) -> PullRequestInfo:
        """Prepare pull request information"""
        # Get changed files
        status = self.get_status()
        changed_files = (
            status.get("modified", []) + 
            status.get("added", []) + 
            status.get("deleted", [])
        )
        
        # Generate body
        if not description:
            description = f"""
## Changes Made by Dive AI

This PR was automatically generated by Dive AI Multi-Agent Coordinator.

### Changed Files
{chr(10).join(f'- `{f}`' for f in changed_files[:20])}
{'...' if len(changed_files) > 20 else ''}

### Summary
- Files changed: {len(changed_files)}
- Generated at: {datetime.now().isoformat()}
"""
        
        return PullRequestInfo(
            title=f"[DiveAI] {title}",
            body=description,
            branch=self.get_current_branch(),
            base_branch=self.config.branch,
            files_changed=changed_files
        )
    
    def auto_commit_and_push(self, task_description: str, 
                             files: List[str] = None) -> CommitResult:
        """
        Automated workflow: stage, commit, and push
        Used by agents to deploy their changes
        """
        # Generate commit message
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        message = f"{task_description} ({timestamp})"
        
        # Commit
        result = self.commit(message, files=files, stage_all=files is None)
        
        if result.success and self.config.auto_push:
            pushed = self.push()
            if pushed:
                result.message += " [pushed]"
        
        return result


def create_deployer(repo_path: str, **kwargs) -> AutoDeployer:
    """Create deployer with default config"""
    config = GitConfig(repo_path=repo_path, **kwargs)
    return AutoDeployer(config)


if __name__ == "__main__":
    print("\n🚀 Auto Deploy Module")
    print("\nUsage:")
    print('   deployer = create_deployer("D:/your/repo")')
    print('   deployer.commit("Fix bug in API")')
    print('   deployer.push()')
    
    # Test with Dive AI repo if exists
    dive_ai_path = "D:\\Antigravity\\Dive AI"
    if os.path.exists(os.path.join(dive_ai_path, ".git")):
        print(f"\n📂 Testing with: {dive_ai_path}")
        deployer = create_deployer(dive_ai_path, auto_push=False)
        
        status = deployer.get_status()
        print(f"\n📊 Status: {json.dumps(status, indent=2)}")
        
        last_commit = deployer.get_last_commit()
        print(f"\n📝 Last commit: {last_commit}")
