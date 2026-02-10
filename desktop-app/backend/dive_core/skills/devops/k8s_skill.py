"""Kubernetes Skill — K8s cluster management via kubectl."""
import subprocess, json
from ..base_skill import BaseSkill
from ...algorithms.base import AlgorithmResult
from ..skill_spec import SkillSpec, SkillCategory

class K8sSkill(BaseSkill):
    def _build_spec(self):
        return SkillSpec(name="k8s-manager", description="Kubernetes: pods, deployments, services, logs, scale",
            category=SkillCategory.DEVOPS, version="1.0.0",
            input_schema={"action": {"type": "string", "required": True}, "namespace": {"type": "string"},
                          "resource": {"type": "string"}, "name": {"type": "string"}, "replicas": {"type": "integer"}},
            output_schema={"items": "list", "output": "string"},
            tags=["k8s", "kubernetes", "pod", "deploy", "container", "cluster", "kubectl"],
            trigger_patterns=[r"k8s\s+", r"kubernetes", r"pod\s+", r"deploy\s+to\s+k8s", r"kubectl"],
            combo_compatible=["docker-ops", "ci-cd", "telegram-bot", "slack-bot"],
            combo_position="end")

    def _kubectl(self, args, timeout=15):
        cmd = ["kubectl"] + args
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return r

    def _execute(self, inputs, context=None):
        action = inputs.get("action", "pods")
        ns = inputs.get("namespace", "default")
        name = inputs.get("name", "")
        resource = inputs.get("resource", "pods")

        try:
            if action == "pods":
                r = self._kubectl(["get", "pods", "-n", ns, "-o", "json"])
                if r.returncode == 0:
                    data = json.loads(r.stdout)
                    pods = [{"name": p["metadata"]["name"], "status": p["status"]["phase"],
                             "ready": sum(1 for c in p["status"].get("containerStatuses", []) if c.get("ready")),
                             "restarts": sum(c.get("restartCount", 0) for c in p["status"].get("containerStatuses", []))}
                            for p in data.get("items", [])]
                    return AlgorithmResult("success", {"pods": pods, "total": len(pods), "namespace": ns},
                                           {"skill": "k8s-manager"})
                return AlgorithmResult("failure", None, {"error": r.stderr[:500]})

            elif action == "deployments":
                r = self._kubectl(["get", "deployments", "-n", ns, "-o", "json"])
                if r.returncode == 0:
                    data = json.loads(r.stdout)
                    deps = [{"name": d["metadata"]["name"],
                             "replicas": d["status"].get("readyReplicas", 0),
                             "desired": d["spec"].get("replicas", 0)}
                            for d in data.get("items", [])]
                    return AlgorithmResult("success", {"deployments": deps, "namespace": ns},
                                           {"skill": "k8s-manager"})

            elif action == "services":
                r = self._kubectl(["get", "services", "-n", ns, "-o", "json"])
                if r.returncode == 0:
                    data = json.loads(r.stdout)
                    svcs = [{"name": s["metadata"]["name"], "type": s["spec"].get("type"),
                             "cluster_ip": s["spec"].get("clusterIP"),
                             "ports": [{"port": p.get("port"), "target": p.get("targetPort")}
                                       for p in s["spec"].get("ports", [])]}
                            for s in data.get("items", [])]
                    return AlgorithmResult("success", {"services": svcs, "namespace": ns},
                                           {"skill": "k8s-manager"})

            elif action == "logs":
                r = self._kubectl(["logs", name, "-n", ns, "--tail=100"])
                return AlgorithmResult("success" if r.returncode == 0 else "failure",
                    {"logs": r.stdout[-3000:], "pod": name}, {"skill": "k8s-manager"})

            elif action == "scale":
                replicas = inputs.get("replicas", 1)
                r = self._kubectl(["scale", f"deployment/{name}", f"--replicas={replicas}", "-n", ns])
                return AlgorithmResult("success" if r.returncode == 0 else "failure",
                    {"scaled": name, "replicas": replicas}, {"skill": "k8s-manager"})

            elif action == "apply":
                file_path = inputs.get("file", "")
                r = self._kubectl(["apply", "-f", file_path, "-n", ns])
                return AlgorithmResult("success" if r.returncode == 0 else "failure",
                    {"applied": file_path, "output": r.stdout[:1000]}, {"skill": "k8s-manager"})

            elif action == "namespaces":
                r = self._kubectl(["get", "namespaces", "-o", "json"])
                if r.returncode == 0:
                    data = json.loads(r.stdout)
                    nss = [n["metadata"]["name"] for n in data.get("items", [])]
                    return AlgorithmResult("success", {"namespaces": nss}, {"skill": "k8s-manager"})

            return AlgorithmResult("failure", None, {"error": f"Unknown action: {action}"})
        except FileNotFoundError:
            return AlgorithmResult("failure", None, {"error": "kubectl not installed"})
        except Exception as e:
            return AlgorithmResult("failure", None, {"error": str(e)})
