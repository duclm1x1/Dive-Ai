"""
Dive AI Desktop - Supabase Client
Cloud database integration for Desktop app

Features:
- User authentication
- Workspace management
- Conversation sync
- Algorithm portfolio sync
- Memory snapshot sync
"""

import os
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    print("⚠️ supabase-py not installed. Run: pip install supabase")


class SupabaseClient:
    """Supabase cloud database client for Dive AI Desktop"""
    
    def __init__(self, url: str = None, key: str = None, config_path: str = None):
        """
        Initialize Supabase client
        
        Args:
            url: Supabase project URL
            key: Supabase anon/service key
            config_path: Path to config file with credentials
        """
        self.client: Optional[Client] = None
        self.user = None
        self.workspace_id = None
        
        # Try to load from config or env
        if not url or not key:
            url, key = self._load_credentials(config_path)
        
        if url and key and SUPABASE_AVAILABLE:
            try:
                self.client = create_client(url, key)
                print(f"☁️ Supabase connected: {url[:30]}...")
            except Exception as e:
                print(f"❌ Supabase connection failed: {e}")
                self.client = None
        else:
            print("⚠️ Supabase not configured - running in offline mode")
    
    def _load_credentials(self, config_path: str = None) -> tuple:
        """Load Supabase credentials from config or environment"""
        # Try environment variables first
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_ANON_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        if url and key:
            return url, key
        
        # Try config file
        config_paths = [
            config_path,
            "config/supabase.json",
            "../config/supabase.json",
            os.path.expanduser("~/.dive-ai/supabase.json")
        ]
        
        for path in config_paths:
            if path and os.path.exists(path):
                try:
                    with open(path, 'r') as f:
                        config = json.load(f)
                    return config.get("url"), config.get("anon_key") or config.get("key")
                except:
                    continue
        
        return None, None
    
    @property
    def is_connected(self) -> bool:
        """Check if Supabase is connected"""
        return self.client is not None
    
    # ==========================================
    # AUTHENTICATION
    # ==========================================
    
    def sign_in(self, email: str, password: str) -> Dict[str, Any]:
        """Sign in with email/password"""
        if not self.client:
            return {"error": "Supabase not connected"}
        
        try:
            response = self.client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            self.user = response.user
            return {"user": self.user, "session": response.session}
        except Exception as e:
            return {"error": str(e)}
    
    def sign_up(self, email: str, password: str, full_name: str = "") -> Dict[str, Any]:
        """Create new account"""
        if not self.client:
            return {"error": "Supabase not connected"}
        
        try:
            response = self.client.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": {"full_name": full_name}
                }
            })
            return {"user": response.user}
        except Exception as e:
            return {"error": str(e)}
    
    def sign_out(self) -> Dict[str, Any]:
        """Sign out current user"""
        if not self.client:
            return {"error": "Supabase not connected"}
        
        try:
            self.client.auth.sign_out()
            self.user = None
            return {"success": True}
        except Exception as e:
            return {"error": str(e)}
    
    def get_user(self) -> Optional[Dict]:
        """Get current authenticated user"""
        if not self.client:
            return None
        
        try:
            return self.client.auth.get_user()
        except:
            return None
    
    # ==========================================
    # WORKSPACES
    # ==========================================
    
    def get_workspaces(self) -> List[Dict]:
        """Get all workspaces for current user"""
        if not self.client:
            return []
        
        try:
            response = self.client.table("workspaces").select(
                "*, workspace_members!inner(user_id, role)"
            ).execute()
            return response.data
        except Exception as e:
            print(f"Error getting workspaces: {e}")
            return []
    
    def create_workspace(self, name: str, description: str = "") -> Dict[str, Any]:
        """Create a new workspace"""
        if not self.client or not self.user:
            return {"error": "Not authenticated"}
        
        try:
            slug = name.lower().replace(" ", "-")
            response = self.client.table("workspaces").insert({
                "owner_id": self.user.id,
                "name": name,
                "slug": slug,
                "description": description
            }).execute()
            return {"workspace": response.data[0]}
        except Exception as e:
            return {"error": str(e)}
    
    def set_workspace(self, workspace_id: str):
        """Set active workspace for subsequent operations"""
        self.workspace_id = workspace_id
    
    # ==========================================
    # CONVERSATIONS
    # ==========================================
    
    def get_conversations(self, limit: int = 50) -> List[Dict]:
        """Get conversations in current workspace"""
        if not self.client or not self.workspace_id:
            return []
        
        try:
            response = self.client.table("conversations") \
                .select("*") \
                .eq("workspace_id", self.workspace_id) \
                .order("updated_at", desc=True) \
                .limit(limit) \
                .execute()
            return response.data
        except Exception as e:
            print(f"Error getting conversations: {e}")
            return []
    
    def create_conversation(self, title: str, model: str = "gpt-4") -> Dict[str, Any]:
        """Create a new conversation"""
        if not self.client or not self.workspace_id or not self.user:
            return {"error": "Not authenticated or no workspace selected"}
        
        try:
            response = self.client.table("conversations").insert({
                "workspace_id": self.workspace_id,
                "user_id": self.user.id,
                "title": title,
                "model": model
            }).execute()
            return {"conversation": response.data[0]}
        except Exception as e:
            return {"error": str(e)}
    
    def save_message(self, conversation_id: str, sender: str, content: str, 
                     metadata: Dict = None) -> Dict[str, Any]:
        """Save a message to conversation"""
        if not self.client:
            return {"error": "Supabase not connected"}
        
        try:
            response = self.client.table("messages").insert({
                "conversation_id": conversation_id,
                "user_id": self.user.id if self.user else None,
                "sender": sender,
                "content": content,
                "metadata": metadata or {}
            }).execute()
            return {"message": response.data[0]}
        except Exception as e:
            return {"error": str(e)}
    
    def get_messages(self, conversation_id: str, limit: int = 100) -> List[Dict]:
        """Get messages in a conversation"""
        if not self.client:
            return []
        
        try:
            response = self.client.table("messages") \
                .select("*") \
                .eq("conversation_id", conversation_id) \
                .order("created_at", desc=False) \
                .limit(limit) \
                .execute()
            return response.data
        except Exception as e:
            print(f"Error getting messages: {e}")
            return []
    
    # ==========================================
    # ALGORITHMS (V29)
    # ==========================================
    
    def sync_algorithms(self, algorithms: List[Dict]) -> Dict[str, Any]:
        """Sync local algorithm portfolio to cloud"""
        if not self.client or not self.workspace_id:
            return {"error": "Not authenticated or no workspace"}
        
        try:
            # Upsert algorithms
            for algo in algorithms:
                algo["workspace_id"] = self.workspace_id
            
            response = self.client.table("algorithms").upsert(
                algorithms,
                on_conflict="workspace_id,algorithm_id"
            ).execute()
            
            return {"synced": len(response.data)}
        except Exception as e:
            return {"error": str(e)}
    
    def get_algorithms(self, tier: str = None) -> List[Dict]:
        """Get algorithms from cloud"""
        if not self.client or not self.workspace_id:
            return []
        
        try:
            query = self.client.table("algorithms") \
                .select("*") \
                .eq("workspace_id", self.workspace_id)
            
            if tier:
                query = query.eq("tier", tier)
            
            response = query.order("success_rate", desc=True).execute()
            return response.data
        except Exception as e:
            print(f"Error getting algorithms: {e}")
            return []
    
    # ==========================================
    # EXECUTION HISTORY (GPA Scoring)
    # ==========================================
    
    def log_execution(self, algorithm_id: str, execution_id: str,
                      gpa_score: float = None, goal_alignment: float = None,
                      plan_alignment: float = None, action_quality: float = None,
                      status: str = "success", input_data: Dict = None,
                      output_data: Dict = None, duration_ms: int = None,
                      tactical_feedback: str = None) -> Dict[str, Any]:
        """Log algorithm execution with GPA score"""
        if not self.client or not self.workspace_id:
            return {"error": "Not authenticated or no workspace"}
        
        try:
            response = self.client.table("execution_history").insert({
                "workspace_id": self.workspace_id,
                "algorithm_id": algorithm_id,
                "execution_id": execution_id,
                "gpa_score": gpa_score,
                "goal_alignment": goal_alignment,
                "plan_alignment": plan_alignment,
                "action_quality": action_quality,
                "status": status,
                "input_data": input_data or {},
                "output_data": output_data or {},
                "duration_ms": duration_ms,
                "tactical_feedback": tactical_feedback,
                "completed_at": datetime.now().isoformat() if status in ["success", "failed"] else None
            }).execute()
            return {"execution": response.data[0]}
        except Exception as e:
            return {"error": str(e)}
    
    def get_execution_history(self, algorithm_id: str = None, 
                               limit: int = 100) -> List[Dict]:
        """Get execution history"""
        if not self.client or not self.workspace_id:
            return []
        
        try:
            query = self.client.table("execution_history") \
                .select("*") \
                .eq("workspace_id", self.workspace_id)
            
            if algorithm_id:
                query = query.eq("algorithm_id", algorithm_id)
            
            response = query.order("created_at", desc=True).limit(limit).execute()
            return response.data
        except Exception as e:
            print(f"Error getting execution history: {e}")
            return []
    
    # ==========================================
    # MEMORY SYNC
    # ==========================================
    
    def sync_memory_snapshot(self, project_name: str, full_content: str,
                             criteria_content: str = None, 
                             changelog_content: str = None) -> Dict[str, Any]:
        """Sync local memory to cloud"""
        if not self.client or not self.workspace_id:
            return {"error": "Not authenticated or no workspace"}
        
        try:
            response = self.client.table("memory_snapshots").upsert({
                "workspace_id": self.workspace_id,
                "snapshot_type": "project",
                "project_name": project_name,
                "full_content": full_content,
                "criteria_content": criteria_content,
                "changelog_content": changelog_content,
                "sync_status": "synced",
                "last_synced_at": datetime.now().isoformat()
            }, on_conflict="workspace_id,project_name").execute()
            
            return {"snapshot": response.data[0] if response.data else None}
        except Exception as e:
            return {"error": str(e)}
    
    def get_memory_snapshot(self, project_name: str) -> Optional[Dict]:
        """Get memory snapshot from cloud"""
        if not self.client or not self.workspace_id:
            return None
        
        try:
            response = self.client.table("memory_snapshots") \
                .select("*") \
                .eq("workspace_id", self.workspace_id) \
                .eq("project_name", project_name) \
                .single() \
                .execute()
            return response.data
        except:
            return None
    
    # ==========================================
    # API USAGE TRACKING
    # ==========================================
    
    def log_api_usage(self, provider: str, model: str, 
                      prompt_tokens: int, completion_tokens: int,
                      latency_ms: int = None, status: str = "success") -> Dict[str, Any]:
        """Log API usage for cost tracking"""
        if not self.client or not self.workspace_id:
            return {"error": "Not authenticated or no workspace"}
        
        # Estimate cost (rough USD cents)
        cost_per_1k = {
            "gpt-4": (3.0, 6.0),
            "gpt-4-turbo": (1.0, 3.0),
            "gpt-3.5-turbo": (0.05, 0.15),
            "claude-3-opus": (15.0, 75.0),
            "claude-3-sonnet": (3.0, 15.0),
            "claude-3-haiku": (0.25, 1.25),
        }
        
        rates = cost_per_1k.get(model, (1.0, 2.0))
        cost_cents = (prompt_tokens / 1000 * rates[0]) + (completion_tokens / 1000 * rates[1])
        
        try:
            response = self.client.table("api_usage").insert({
                "workspace_id": self.workspace_id,
                "user_id": self.user.id if self.user else None,
                "provider": provider,
                "model": model,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens,
                "cost_cents": round(cost_cents, 4),
                "latency_ms": latency_ms,
                "status": status
            }).execute()
            return {"usage": response.data[0]}
        except Exception as e:
            return {"error": str(e)}


# ==========================================
# SINGLETON INSTANCE
# ==========================================

_supabase_client: Optional[SupabaseClient] = None

def get_supabase_client() -> SupabaseClient:
    """Get or create Supabase client singleton"""
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = SupabaseClient()
    return _supabase_client

def init_supabase(url: str = None, key: str = None) -> SupabaseClient:
    """Initialize Supabase with custom credentials"""
    global _supabase_client
    _supabase_client = SupabaseClient(url=url, key=key)
    return _supabase_client


# ==========================================
# CLI TESTING
# ==========================================

if __name__ == "__main__":
    print("🔌 Testing Supabase Client")
    print("=" * 50)
    
    client = get_supabase_client()
    
    if client.is_connected:
        print("✅ Supabase connected!")
        
        # Test workspace listing
        workspaces = client.get_workspaces()
        print(f"📁 Workspaces: {len(workspaces)}")
        
    else:
        print("⚠️ Running in offline mode")
        print("To connect, set environment variables:")
        print("  SUPABASE_URL=https://your-project.supabase.co")
        print("  SUPABASE_ANON_KEY=your-key")
