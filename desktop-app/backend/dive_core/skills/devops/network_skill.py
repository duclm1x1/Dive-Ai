"""Network Tools Skill — ping, DNS lookup, port scan, HTTP check."""
import subprocess, socket, urllib.request, json, time
from ..base_skill import BaseSkill
from ...algorithms.base import AlgorithmResult
from ..skill_spec import SkillSpec, SkillCategory

class NetworkSkill(BaseSkill):
    def _build_spec(self):
        return SkillSpec(name="network-tools", description="Network utilities: ping, DNS, port scan, HTTP check, IP info",
            category=SkillCategory.SYSTEM, version="1.0.0",
            input_schema={"action": {"type": "string", "required": True}, "host": {"type": "string"},
                          "port": {"type": "integer"}, "ports": {"type": "string"}},
            output_schema={"result": "dict", "reachable": "boolean"},
            tags=["network", "ping", "dns", "port", "scan", "http", "ip", "traceroute"],
            trigger_patterns=[r"ping\s+", r"dns\s+", r"port\s+scan", r"check\s+(host|server)", r"network\s+"],
            combo_compatible=["system-info", "telegram-bot", "scheduler"],
            combo_position="start")

    def _execute(self, inputs, context=None):
        action = inputs.get("action", "ping")
        host = inputs.get("host", "8.8.8.8")

        try:
            if action == "ping":
                cmd = ["ping", "-n", "4", host]  # Windows: -n, Linux: -c
                r = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
                lines = r.stdout.strip().split("\n")
                # Extract stats from last lines
                stats = {}
                for line in lines[-3:]:
                    if "Minimum" in line or "Average" in line or "min" in line:
                        stats["summary"] = line.strip()
                return AlgorithmResult("success", {
                    "host": host, "reachable": r.returncode == 0,
                    "output": r.stdout[-1000:], "stats": stats,
                }, {"skill": "network-tools"})

            elif action == "dns":
                ip = socket.gethostbyname(host)
                try:
                    reverse = socket.gethostbyaddr(ip)[0]
                except:
                    reverse = "N/A"
                # Get all addresses
                addrs = socket.getaddrinfo(host, None)
                ips = list(set(a[4][0] for a in addrs))
                return AlgorithmResult("success", {
                    "host": host, "ip": ip, "reverse": reverse,
                    "all_ips": ips[:10],
                }, {"skill": "network-tools"})

            elif action == "port-scan":
                port = inputs.get("port", 0)
                ports_str = inputs.get("ports", "")
                if port:
                    ports_to_scan = [port]
                elif ports_str:
                    ports_to_scan = [int(p.strip()) for p in ports_str.split(",")]
                else:
                    ports_to_scan = [22, 80, 443, 3000, 3306, 5432, 6379, 8080, 8443, 9090]

                results = []
                for p in ports_to_scan[:20]:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(1)
                    try:
                        result = s.connect_ex((host, p))
                        results.append({"port": p, "open": result == 0})
                    except:
                        results.append({"port": p, "open": False})
                    finally:
                        s.close()

                open_ports = [r["port"] for r in results if r["open"]]
                return AlgorithmResult("success", {
                    "host": host, "ports": results, "open_ports": open_ports,
                    "total_scanned": len(results),
                }, {"skill": "network-tools"})

            elif action == "http-check":
                start = time.time()
                url = host if host.startswith("http") else f"https://{host}"
                req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "DiveAI/29.7"})
                with urllib.request.urlopen(req, timeout=10) as resp:
                    latency = round((time.time() - start) * 1000, 1)
                    return AlgorithmResult("success", {
                        "url": url, "status": resp.status, "latency_ms": latency,
                        "headers": dict(list(resp.headers.items())[:10]),
                    }, {"skill": "network-tools"})

            elif action == "ip-info":
                url = f"https://ipapi.co/{host}/json/" if host != "self" else "https://ipapi.co/json/"
                req = urllib.request.Request(url, headers={"User-Agent": "DiveAI/29.7"})
                with urllib.request.urlopen(req, timeout=10) as resp:
                    data = json.loads(resp.read())
                return AlgorithmResult("success", {
                    "ip": data.get("ip"), "city": data.get("city"), "region": data.get("region"),
                    "country": data.get("country_name"), "org": data.get("org"),
                    "timezone": data.get("timezone"),
                }, {"skill": "network-tools"})

            elif action == "traceroute":
                cmd = ["tracert", "-d", "-h", "15", host]  # Windows
                r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                return AlgorithmResult("success", {"host": host, "output": r.stdout[-3000:]},
                                       {"skill": "network-tools"})

            return AlgorithmResult("failure", None, {"error": "action: ping/dns/port-scan/http-check/ip-info/traceroute"})
        except Exception as e:
            return AlgorithmResult("failure", None, {"error": str(e)})
