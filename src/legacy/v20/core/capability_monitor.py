#!/usr/bin/env python3
"""
Dive AI V20 - Advanced Capability Monitoring System
Tracks which capabilities each agent is actually using
"""

import json
import time
from datetime import datetime
from collections import defaultdict

CAPABILITY_FILE = "/tmp/dive_ai_capabilities.json"

class CapabilityMonitor:
    """Monitor and track agent capability usage"""
    
    CAPABILITIES = {
        'skills': [
            'web_developer', 'backend_engineer', 'frontend_engineer', 'devops_engineer',
            'database_architect', 'api_designer', 'security_expert', 'test_engineer',
            'ml_engineer', 'data_scientist', 'cloud_architect', 'mobile_developer'
        ],
        'tools': [
            'RAG_search', 'semantic_search', 'code_search', 'doc_search',
            'MCP_filesystem', 'MCP_terminal', 'MCP_browser', 'MCP_database',
            'dive_memory_read', 'dive_memory_write', 'knowledge_graph'
        ],
        'features': [
            'streaming', 'function_calling', 'vision', 'code_execution',
            'multi_provider', 'failover', 'cost_optimization'
        ]
    }
    
    def __init__(self):
        self.agent_capabilities = defaultdict(lambda: {
            'skills_used': set(),
            'tools_used': set(),
            'features_used': set(),
            'memory_accessed': False,
            'rag_queries': 0,
            'mcp_calls': 0,
            'start_time': None,
            'end_time': None
        })
    
    def track_skill(self, agent_id: int, skill: str):
        """Track skill activation"""
        self.agent_capabilities[agent_id]['skills_used'].add(skill)
        self._write_state()
    
    def track_tool(self, agent_id: int, tool: str):
        """Track tool usage"""
        self.agent_capabilities[agent_id]['tools_used'].add(tool)
        
        if 'RAG' in tool or 'search' in tool:
            self.agent_capabilities[agent_id]['rag_queries'] += 1
        if 'MCP' in tool:
            self.agent_capabilities[agent_id]['mcp_calls'] += 1
        if 'memory' in tool:
            self.agent_capabilities[agent_id]['memory_accessed'] = True
        
        self._write_state()
    
    def track_feature(self, agent_id: int, feature: str):
        """Track feature usage"""
        self.agent_capabilities[agent_id]['features_used'].add(feature)
        self._write_state()
    
    def start_agent(self, agent_id: int):
        """Mark agent start"""
        self.agent_capabilities[agent_id]['start_time'] = datetime.now().isoformat()
        self._write_state()
    
    def end_agent(self, agent_id: int):
        """Mark agent end"""
        self.agent_capabilities[agent_id]['end_time'] = datetime.now().isoformat()
        self._write_state()
    
    def get_utilization_stats(self):
        """Calculate capability utilization statistics"""
        total_agents = len(self.agent_capabilities)
        if total_agents == 0:
            return {}
        
        stats = {
            'total_agents': total_agents,
            'skills': defaultdict(int),
            'tools': defaultdict(int),
            'features': defaultdict(int),
            'agents_using_memory': 0,
            'agents_using_rag': 0,
            'agents_using_mcp': 0,
            'total_rag_queries': 0,
            'total_mcp_calls': 0,
            'utilization_percentage': {}
        }
        
        for agent_id, caps in self.agent_capabilities.items():
            # Count skill usage
            for skill in caps['skills_used']:
                stats['skills'][skill] += 1
            
            # Count tool usage
            for tool in caps['tools_used']:
                stats['tools'][tool] += 1
            
            # Count feature usage
            for feature in caps['features_used']:
                stats['features'][feature] += 1
            
            # Count memory/RAG/MCP usage
            if caps['memory_accessed']:
                stats['agents_using_memory'] += 1
            if caps['rag_queries'] > 0:
                stats['agents_using_rag'] += 1
                stats['total_rag_queries'] += caps['rag_queries']
            if caps['mcp_calls'] > 0:
                stats['agents_using_mcp'] += 1
                stats['total_mcp_calls'] += caps['mcp_calls']
        
        # Calculate utilization percentages
        stats['utilization_percentage'] = {
            'memory': (stats['agents_using_memory'] / total_agents) * 100,
            'rag': (stats['agents_using_rag'] / total_agents) * 100,
            'mcp': (stats['agents_using_mcp'] / total_agents) * 100,
            'skills': (len([a for a in self.agent_capabilities.values() if a['skills_used']]) / total_agents) * 100,
            'tools': (len([a for a in self.agent_capabilities.values() if a['tools_used']]) / total_agents) * 100
        }
        
        return stats
    
    def _write_state(self):
        """Write current state to file"""
        try:
            # Convert sets to lists for JSON serialization
            serializable = {}
            for agent_id, caps in self.agent_capabilities.items():
                serializable[str(agent_id)] = {
                    'skills_used': list(caps['skills_used']),
                    'tools_used': list(caps['tools_used']),
                    'features_used': list(caps['features_used']),
                    'memory_accessed': caps['memory_accessed'],
                    'rag_queries': caps['rag_queries'],
                    'mcp_calls': caps['mcp_calls'],
                    'start_time': caps['start_time'],
                    'end_time': caps['end_time']
                }
            
            with open(CAPABILITY_FILE, 'w') as f:
                json.dump({
                    'agents': serializable,
                    'stats': self.get_utilization_stats(),
                    'last_update': datetime.now().isoformat()
                }, f, indent=2, default=str)
        except Exception as e:
            pass  # Silent fail

def display_capability_dashboard():
    """Display real-time capability usage dashboard"""
    import os
    
    while True:
        try:
            if not os.path.exists(CAPABILITY_FILE):
                print("Waiting for capability data...")
                time.sleep(2)
                continue
            
            with open(CAPABILITY_FILE, 'r') as f:
                data = json.load(f)
            
            stats = data.get('stats', {})
            agents = data.get('agents', {})
            
            os.system('clear' if os.name != 'nt' else 'cls')
            
            print("=" * 100)
            print("DIVE AI V20 - CAPABILITY UTILIZATION DASHBOARD")
            print("=" * 100)
            print(f"Total Agents: {stats.get('total_agents', 0)}")
            print(f"Last Update: {data.get('last_update', 'N/A')}")
            print("=" * 100)
            
            # Utilization percentages
            util = stats.get('utilization_percentage', {})
            print("\n📊 CAPABILITY UTILIZATION:")
            print(f"  Dive Memory:  {util.get('memory', 0):.1f}% ({stats.get('agents_using_memory', 0)} agents)")
            print(f"  RAG Search:   {util.get('rag', 0):.1f}% ({stats.get('agents_using_rag', 0)} agents, {stats.get('total_rag_queries', 0)} queries)")
            print(f"  MCP Tools:    {util.get('mcp', 0):.1f}% ({stats.get('agents_using_mcp', 0)} agents, {stats.get('total_mcp_calls', 0)} calls)")
            print(f"  Skills:       {util.get('skills', 0):.1f}% (agents using specialized skills)")
            print(f"  Tools:        {util.get('tools', 0):.1f}% (agents using advanced tools)")
            
            # Top skills
            skills = stats.get('skills', {})
            if skills:
                print("\n🎯 TOP SKILLS USED:")
                sorted_skills = sorted(skills.items(), key=lambda x: x[1], reverse=True)[:10]
                for skill, count in sorted_skills:
                    print(f"  {skill:25s} {count:3d} agents")
            
            # Top tools
            tools = stats.get('tools', {})
            if tools:
                print("\n🛠️  TOP TOOLS USED:")
                sorted_tools = sorted(tools.items(), key=lambda x: x[1], reverse=True)[:10]
                for tool, count in sorted_tools:
                    print(f"  {tool:25s} {count:3d} agents")
            
            # Agent details (first 10)
            print("\n🤖 AGENT CAPABILITY DETAILS (First 10):")
            print("-" * 100)
            for i, (agent_id, caps) in enumerate(list(agents.items())[:10]):
                skills_str = ", ".join(caps.get('skills_used', [])[:3]) or "None"
                tools_str = ", ".join(caps.get('tools_used', [])[:3]) or "None"
                print(f"  Agent #{agent_id:3s} | Skills: {skills_str:30s} | Tools: {tools_str:30s}")
            
            print("=" * 100)
            print("Press Ctrl+C to exit")
            print("=" * 100)
            
            time.sleep(2)
        
        except KeyboardInterrupt:
            print("\n\nMonitoring stopped.")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(2)

if __name__ == "__main__":
    display_capability_dashboard()
