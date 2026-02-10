"""Crypto Tracker Skill — Cryptocurrency prices via CoinGecko."""
import urllib.request, json
from ..base_skill import BaseSkill
from ...algorithms.base import AlgorithmResult
from ..skill_spec import SkillSpec, SkillCategory

class CryptoSkill(BaseSkill):
    def _build_spec(self):
        return SkillSpec(name="crypto-tracker", description="Track crypto prices: BTC, ETH, and more",
            category=SkillCategory.FINANCE, version="1.0.0",
            input_schema={"coin": {"type": "string", "required": True}, "currency": {"type": "string"}},
            output_schema={"price": "float", "change_24h": "float", "market_cap": "float"},
            tags=["crypto", "bitcoin", "ethereum", "price", "coin", "blockchain"],
            trigger_patterns=[r"crypto\s+", r"bitcoin", r"btc", r"eth", r"coin\s+price"],
            combo_compatible=["data-analyzer", "telegram-bot", "scheduler"],
            combo_position="start")

    def _execute(self, inputs, context=None):
        coin = inputs.get("coin", "bitcoin").lower()
        currency = inputs.get("currency", "usd").lower()
        
        try:
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin}&vs_currencies={currency}&include_24hr_change=true&include_market_cap=true"
            req = urllib.request.Request(url, headers={"User-Agent": "DiveAI/29.7"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read())
            
            coin_data = data.get(coin, {})
            if not coin_data:
                return AlgorithmResult("failure", None, {"error": f"Coin '{coin}' not found"})
            
            return AlgorithmResult("success", {
                "coin": coin, "currency": currency,
                "price": coin_data.get(currency, 0),
                "change_24h": round(coin_data.get(f"{currency}_24h_change", 0), 2),
                "market_cap": coin_data.get(f"{currency}_market_cap", 0),
            }, {"skill": "crypto-tracker"})
        except Exception as e:
            return AlgorithmResult("failure", None, {"error": str(e)})
