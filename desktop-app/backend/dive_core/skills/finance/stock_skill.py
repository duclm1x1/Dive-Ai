"""Stock Tracker Skill — Real-time stock prices and analysis."""
import urllib.request, json, os, time
from ..base_skill import BaseSkill
from ...algorithms.base import AlgorithmResult
from ..skill_spec import SkillSpec, SkillCategory

class StockSkill(BaseSkill):
    def _build_spec(self):
        return SkillSpec(name="stock-tracker", description="Track stock prices, get quotes, basic analysis",
            category=SkillCategory.FINANCE, version="1.0.0",
            input_schema={"symbol": {"type": "string", "required": True}, "action": {"type": "string"}},
            output_schema={"price": "float", "change": "float", "data": "dict"},
            tags=["stock", "price", "market", "invest", "quote", "share", "ticker"],
            trigger_patterns=[r"stock\s+", r"price\s+of", r"ticker\s+", r"market\s+"],
            combo_compatible=["data-analyzer", "telegram-bot", "note-taker", "scheduler"],
            combo_position="start")

    def _execute(self, inputs, context=None):
        symbol = inputs.get("symbol", "AAPL").upper()
        action = inputs.get("action", "quote")
        
        # Use Yahoo Finance v8 (free, no key)
        try:
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range=5d"
            req = urllib.request.Request(url, headers={"User-Agent": "DiveAI/29.7"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read())
            
            result = data.get("chart", {}).get("result", [{}])[0]
            meta = result.get("meta", {})
            price = meta.get("regularMarketPrice", 0)
            prev = meta.get("previousClose", price)
            change = round(price - prev, 2)
            pct = round((change / prev * 100) if prev else 0, 2)
            
            return AlgorithmResult("success", {
                "symbol": symbol, "price": price, "previous_close": prev,
                "change": change, "change_percent": pct,
                "currency": meta.get("currency", "USD"),
                "exchange": meta.get("exchangeName", ""),
                "market_time": meta.get("regularMarketTime", 0),
            }, {"skill": "stock-tracker"})
        except Exception as e:
            return AlgorithmResult("failure", None, {"error": str(e), "symbol": symbol})
