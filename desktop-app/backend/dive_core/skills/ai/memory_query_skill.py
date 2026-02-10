"""Memory Query Skill — Search past conversations and stored facts."""
import os, json, re
from ..base_skill import BaseSkill
from ...algorithms.base import AlgorithmResult
from ..skill_spec import SkillSpec, SkillCategory

class MemoryQuerySkill(BaseSkill):
    def _build_spec(self):
        return SkillSpec(name="memory-query", description="Search memory: past conversations, facts, preferences",
            category=SkillCategory.AI, version="1.0.0",
            input_schema={"query": {"type": "string", "required": True}, "scope": {"type": "string"}},
            output_schema={"results": "list", "total": "integer"},
            tags=["memory", "recall", "remember", "history", "past"],
            trigger_patterns=[r"remember", r"recall", r"what\s+did", r"past\s+conversation", r"memory"],
            combo_compatible=["deep-research", "prompt-optimizer", "note-taker"], combo_position="start")

    def _execute(self, inputs, context=None):
        query = inputs.get("query", "")
        scope = inputs.get("scope", "all")  # "facts", "conversations", "all"
        results = []
        
        memory_dir = os.path.expanduser("~/.dive-ai/memory")
        conv_dir = os.path.expanduser("~/.dive-ai/conversations")
        
        # Search long-term facts
        if scope in ("all", "facts"):
            context_file = os.path.join(memory_dir, "context.json")
            if os.path.exists(context_file):
                try:
                    with open(context_file, "r") as f:
                        facts = json.load(f)
                    for fact in facts if isinstance(facts, list) else [facts]:
                        fact_str = json.dumps(fact) if isinstance(fact, dict) else str(fact)
                        if query.lower() in fact_str.lower():
                            results.append({"type": "fact", "content": fact_str[:300]})
                except: pass
        
        # Search conversation history
        if scope in ("all", "conversations"):
            if os.path.exists(conv_dir):
                for fname in os.listdir(conv_dir):
                    if fname.endswith(".json") and fname != "index.json":
                        try:
                            fpath = os.path.join(conv_dir, fname)
                            with open(fpath, "r", encoding="utf-8") as f:
                                conv = json.load(f)
                            messages = conv.get("messages", []) if isinstance(conv, dict) else conv
                            for msg in (messages if isinstance(messages, list) else []):
                                content = msg.get("content", "") if isinstance(msg, dict) else str(msg)
                                if query.lower() in content.lower():
                                    results.append({"type": "conversation", "file": fname,
                                                    "content": content[:300], "role": msg.get("role", "")})
                        except: pass
        
        return AlgorithmResult("success", {
            "results": results[:20], "total": len(results), "query": query, "scope": scope,
        }, {"skill": "memory-query"})
