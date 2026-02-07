"""
Use Dive Agent to push commits to GitHub via API
"""

import asyncio
import sys
import subprocess
import base64
import requests
from pathlib import Path

sys.path.append('/home/ubuntu/dive-ai-messenger/Dive-Ai')

from integration.unified_llm_client import UnifiedLLMClient, Provider
from core.dive_agent_fleet import DiveAgent, AgentStatus


class GitHubPushAgent(DiveAgent):
    """Dive Agent specialized for GitHub operations"""
    
    def __init__(self, llm_client: UnifiedLLMClient, github_token: str):
        super().__init__(id=0, model="claude-opus-4.5", status=AgentStatus.IDLE)
        self.llm_client = llm_client
        self.github_token = github_token
        self.repo_owner = "duclm1x1"
        self.repo_name = "Dive-Ai"
    
    def get_file_content(self, file_path: str) -> str:
        """Read file content"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"Error reading {file_path}: {e}"
    
    def get_changed_files(self) -> list:
        """Get list of changed files"""
        try:
            result = subprocess.run(
                ['git', 'diff', '--name-only', 'origin/main..HEAD'],
                cwd='/home/ubuntu/dive-ai-messenger/Dive-Ai',
                capture_output=True,
                text=True
            )
            files = result.stdout.strip().split('\n')
            return [f for f in files if f]
        except Exception as e:
            print(f"Error getting changed files: {e}")
            return []
    
    def push_file_to_github(self, file_path: str, content: str, commit_message: str) -> bool:
        """Push a single file to GitHub via API"""
        try:
            # Get current file SHA if it exists
            url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/contents/{file_path}"
            headers = {
                "Authorization": f"Bearer {self.github_token}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            response = requests.get(url, headers=headers)
            sha = None
            if response.status_code == 200:
                sha = response.json().get('sha')
            
            # Encode content to base64
            content_bytes = content.encode('utf-8')
            content_base64 = base64.b64encode(content_bytes).decode('utf-8')
            
            # Push file
            data = {
                "message": commit_message,
                "content": content_base64,
                "branch": "main"
            }
            
            if sha:
                data["sha"] = sha
            
            response = requests.put(url, headers=headers, json=data)
            
            if response.status_code in [200, 201]:
                print(f"✅ Pushed: {file_path}")
                return True
            else:
                print(f"❌ Failed to push {file_path}: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error pushing {file_path}: {e}")
            return False
    
    async def execute_push(self) -> dict:
        """Execute the push operation"""
        print("🚀 Dive Agent #0 starting GitHub push operation")
        print("="*70)
        
        # Get changed files
        files = self.get_changed_files()
        print(f"\n📦 Found {len(files)} files to push:")
        for i, f in enumerate(files, 1):
            print(f"   {i}. {f}")
        
        if not files:
            print("\n⚠️ No files to push")
            return {"status": "no_changes", "files": 0}
        
        print(f"\n🔄 Pushing files to GitHub...")
        print("-"*70)
        
        success_count = 0
        failed_files = []
        
        for file_path in files:
            full_path = f"/home/ubuntu/dive-ai-messenger/Dive-Ai/{file_path}"
            
            # Read file content
            content = self.get_file_content(full_path)
            
            if content.startswith("Error"):
                print(f"⚠️ Skipping {file_path}: {content}")
                failed_files.append(file_path)
                continue
            
            # Push to GitHub
            commit_msg = f"Update {file_path} via Dive Agent"
            success = self.push_file_to_github(file_path, content, commit_msg)
            
            if success:
                success_count += 1
            else:
                failed_files.append(file_path)
            
            # Small delay to avoid rate limiting
            await asyncio.sleep(0.5)
        
        print("-"*70)
        print(f"\n📊 Push Results:")
        print(f"   Total files: {len(files)}")
        print(f"   Successful: {success_count}")
        print(f"   Failed: {len(failed_files)}")
        
        if failed_files:
            print(f"\n❌ Failed files:")
            for f in failed_files:
                print(f"   - {f}")
        
        if success_count == len(files):
            print(f"\n🎉 All files pushed successfully!")
            return {"status": "success", "files": success_count}
        elif success_count > 0:
            print(f"\n⚠️ Partial success")
            return {"status": "partial", "files": success_count, "failed": failed_files}
        else:
            print(f"\n❌ All pushes failed")
            return {"status": "failed", "files": 0}


async def main():
    """Main function"""
    print("\n" + "="*70)
    print("🤖 DIVE AGENT GITHUB PUSH")
    print("="*70)
    
    # Initialize LLM client
    llm_client = UnifiedLLMClient()
    
    # GitHub token
    github_token = "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"
    
    # Create agent
    agent = GitHubPushAgent(llm_client, github_token)
    
    # Execute push
    result = await agent.execute_push()
    
    print("\n" + "="*70)
    if result["status"] == "success":
        print("✅ PUSH COMPLETE - All files synced to GitHub!")
    elif result["status"] == "partial":
        print("⚠️ PUSH PARTIAL - Some files synced to GitHub")
    elif result["status"] == "no_changes":
        print("ℹ️ NO CHANGES - Nothing to push")
    else:
        print("❌ PUSH FAILED - No files synced")
    print("="*70)
    
    return result["status"] == "success"


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
