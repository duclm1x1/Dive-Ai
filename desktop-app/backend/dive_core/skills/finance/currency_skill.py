"""Currency Converter Skill — Real-time exchange rates."""
import urllib.request, json
from ..base_skill import BaseSkill
from ...algorithms.base import AlgorithmResult
from ..skill_spec import SkillSpec, SkillCategory

class CurrencySkill(BaseSkill):
    def _build_spec(self):
        return SkillSpec(name="currency-converter", description="Convert currencies with real-time exchange rates",
            category=SkillCategory.FINANCE, version="1.0.0",
            input_schema={"amount": {"type": "float", "required": True},
                          "from_currency": {"type": "string", "required": True},
                          "to_currency": {"type": "string", "required": True}},
            output_schema={"result": "float", "rate": "float"},
            tags=["currency", "convert", "exchange", "rate", "usd", "eur", "vnd"],
            trigger_patterns=[r"convert\s+", r"exchange\s+rate", r"how\s+much\s+is", r"\d+\s+usd\s+to"],
            combo_compatible=["data-analyzer", "budget-tracker"],
            combo_position="any")

    def _execute(self, inputs, context=None):
        amount = float(inputs.get("amount", 1))
        from_c = inputs.get("from_currency", "USD").upper()
        to_c = inputs.get("to_currency", "VND").upper()
        
        try:
            # Use exchangerate-api (free tier)
            url = f"https://open.er-api.com/v6/latest/{from_c}"
            req = urllib.request.Request(url, headers={"User-Agent": "DiveAI/29.7"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read())
            
            rates = data.get("rates", {})
            if to_c not in rates:
                return AlgorithmResult("failure", None, {"error": f"'{to_c}' not found in rates"})
            
            rate = rates[to_c]
            result = round(amount * rate, 4)
            return AlgorithmResult("success", {
                "amount": amount, "from": from_c, "to": to_c,
                "rate": rate, "result": result,
                "formatted": f"{amount} {from_c} = {result} {to_c}",
            }, {"skill": "currency-converter"})
        except Exception as e:
            return AlgorithmResult("failure", None, {"error": str(e)})
