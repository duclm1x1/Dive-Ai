"""API Testing Skill -- HTTP endpoint testing, load testing, assertions."""
import urllib.request, json, time, statistics
from ..base_skill import BaseSkill
from ...algorithms.base import AlgorithmResult
from ..skill_spec import SkillSpec, SkillCategory

class APITestSkill(BaseSkill):
    def _build_spec(self):
        return SkillSpec(name="api-tester", description="API testing: request, assert, load test, suite",
            category=SkillCategory.DEVOPS, version="1.0.0",
            input_schema={"action": {"type": "string", "required": True}, "url": {"type": "string"},
                          "method": {"type": "string"}, "headers": {"type": "dict"},
                          "body": {"type": "string"}, "expect": {"type": "dict"}, "count": {"type": "integer"}},
            output_schema={"status": "integer", "body": "string", "latency_ms": "float"},
            tags=["api", "test", "http", "rest", "load", "endpoint"],
            trigger_patterns=[r"test\s+api", r"api\s+test", r"load\s+test", r"http\s+test"],
            combo_compatible=["network-tools", "slack-bot", "scheduler"],
            combo_position="any")

    def _req(self, url, method="GET", headers=None, body=None, timeout=15):
        hdrs = {"User-Agent": "DiveAI-APITester/1.0", "Accept": "application/json"}
        if headers: hdrs.update(headers)
        data = body.encode() if isinstance(body, str) else json.dumps(body).encode() if body else None
        if data and "Content-Type" not in hdrs: hdrs["Content-Type"] = "application/json"
        req = urllib.request.Request(url, data=data, headers=hdrs, method=method)
        start = time.time()
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return {"status": resp.status, "body": resp.read().decode("utf-8", errors="replace")[:5000],
                        "headers": dict(resp.headers.items()), "latency_ms": round((time.time()-start)*1000, 1)}
        except urllib.error.HTTPError as e:
            return {"status": e.code, "body": e.read().decode("utf-8", errors="replace")[:2000],
                    "headers": dict(e.headers.items()), "latency_ms": round((time.time()-start)*1000, 1)}

    def _execute(self, inputs, context=None):
        action = inputs.get("action", "request")
        url = inputs.get("url", "")
        method = inputs.get("method", "GET").upper()
        headers = inputs.get("headers", {})
        body = inputs.get("body")
        try:
            if action == "request":
                if not url: return AlgorithmResult("failure", None, {"error": "url required"})
                return AlgorithmResult("success", self._req(url, method, headers, body), {"skill": "api-tester"})

            elif action == "assert":
                if not url: return AlgorithmResult("failure", None, {"error": "url required"})
                expect = inputs.get("expect", {})
                result = self._req(url, method, headers, body)
                checks, passed = [], True
                if "status" in expect:
                    ok = result["status"] == expect["status"]
                    checks.append({"check": "status", "expected": expect["status"], "actual": result["status"], "passed": ok})
                    if not ok: passed = False
                if "contains" in expect:
                    ok = expect["contains"] in result["body"]
                    checks.append({"check": "body_contains", "passed": ok})
                    if not ok: passed = False
                if "max_latency" in expect:
                    ok = result["latency_ms"] <= expect["max_latency"]
                    checks.append({"check": "latency", "actual": result["latency_ms"], "passed": ok})
                    if not ok: passed = False
                return AlgorithmResult("success", {"passed": passed, "assertions": checks,
                    "status": result["status"], "latency_ms": result["latency_ms"]}, {"skill": "api-tester"})

            elif action == "load-test":
                if not url: return AlgorithmResult("failure", None, {"error": "url required"})
                count = min(inputs.get("count", 10), 100)
                latencies, statuses, errors = [], {}, 0
                for _ in range(count):
                    try:
                        r = self._req(url, method, headers, body, timeout=10)
                        latencies.append(r["latency_ms"])
                        s = str(r["status"]); statuses[s] = statuses.get(s, 0) + 1
                    except: errors += 1
                return AlgorithmResult("success", {
                    "requests": count, "errors": errors,
                    "avg_ms": round(statistics.mean(latencies), 1) if latencies else 0,
                    "min_ms": round(min(latencies), 1) if latencies else 0,
                    "max_ms": round(max(latencies), 1) if latencies else 0,
                    "p50_ms": round(statistics.median(latencies), 1) if latencies else 0,
                    "statuses": statuses,
                    "success_rate": round((count-errors)/count*100, 1) if count else 0,
                }, {"skill": "api-tester"})

            return AlgorithmResult("failure", None, {"error": "action: request/assert/load-test"})
        except Exception as e:
            return AlgorithmResult("failure", None, {"error": str(e)})
