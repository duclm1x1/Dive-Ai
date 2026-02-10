"""Budget Tracker Skill — Track income/expenses, calculate balance."""
import json, os, time
from ..base_skill import BaseSkill
from ...algorithms.base import AlgorithmResult
from ..skill_spec import SkillSpec, SkillCategory

class BudgetSkill(BaseSkill):
    def _build_spec(self):
        return SkillSpec(name="budget-tracker", description="Track expenses, income, and budgets",
            category=SkillCategory.FINANCE, version="1.0.0",
            input_schema={"action": {"type": "string", "required": True}, "amount": {"type": "float"},
                          "category": {"type": "string"}, "description": {"type": "string"}},
            output_schema={"entries": "list", "balance": "float", "summary": "dict"},
            tags=["budget", "expense", "income", "money", "spend", "track"],
            trigger_patterns=[r"budget\s+", r"expense", r"income", r"spent\s+", r"add\s+expense"],
            combo_compatible=["data-analyzer", "note-taker", "email-send"],
            combo_position="any")

    def _file(self):
        d = os.path.expanduser("~/.dive-ai/finance")
        os.makedirs(d, exist_ok=True)
        return os.path.join(d, "budget.json")

    def _load(self):
        f = self._file()
        if os.path.exists(f):
            with open(f) as fh: return json.load(fh)
        return []

    def _save(self, entries):
        with open(self._file(), "w") as f: json.dump(entries, f, indent=2)

    def _execute(self, inputs, context=None):
        action = inputs.get("action", "summary")
        entries = self._load()
        
        if action == "add":
            e = {"id": str(int(time.time())), "amount": inputs.get("amount", 0),
                 "type": "expense" if inputs.get("amount", 0) < 0 else "income",
                 "category": inputs.get("category", "general"),
                 "description": inputs.get("description", ""),
                 "date": time.strftime("%Y-%m-%d %H:%M")}
            entries.append(e)
            self._save(entries)
            return AlgorithmResult("success", {"added": e, "total_entries": len(entries)}, {"skill": "budget-tracker"})
        
        elif action == "summary":
            income = sum(e["amount"] for e in entries if e.get("amount", 0) > 0)
            expenses = sum(abs(e["amount"]) for e in entries if e.get("amount", 0) < 0)
            by_cat = {}
            for e in entries:
                cat = e.get("category", "general")
                by_cat[cat] = by_cat.get(cat, 0) + e.get("amount", 0)
            return AlgorithmResult("success", {
                "income": income, "expenses": expenses, "balance": income - expenses,
                "total_entries": len(entries), "by_category": by_cat,
            }, {"skill": "budget-tracker"})
        
        elif action == "list":
            return AlgorithmResult("success", {"entries": entries[-20:], "total": len(entries)},
                                   {"skill": "budget-tracker"})
        
        return AlgorithmResult("failure", None, {"error": "action: add/summary/list"})
