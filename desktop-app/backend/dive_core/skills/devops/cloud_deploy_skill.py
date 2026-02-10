"""Cloud Deploy Skill — AWS/GCP/Azure simple operations."""
import subprocess, json, os
from ..base_skill import BaseSkill
from ...algorithms.base import AlgorithmResult
from ..skill_spec import SkillSpec, SkillCategory

class CloudDeploySkill(BaseSkill):
    def _build_spec(self):
        return SkillSpec(name="cloud-deploy", description="Cloud operations: AWS S3/EC2, GCP, Azure basics",
            category=SkillCategory.DEVOPS, version="1.0.0",
            input_schema={"provider": {"type": "string", "required": True}, "action": {"type": "string", "required": True},
                          "bucket": {"type": "string"}, "file": {"type": "string"}, "region": {"type": "string"}},
            output_schema={"result": "dict", "output": "string"},
            tags=["cloud", "aws", "gcp", "azure", "s3", "deploy", "ec2", "lambda"],
            trigger_patterns=[r"deploy\s+to\s+(aws|gcp|cloud)", r"s3\s+", r"upload\s+to\s+cloud", r"cloud\s+"],
            combo_compatible=["ci-cd", "docker-ops", "k8s-manager", "telegram-bot"],
            combo_position="end")

    def _run(self, cmd, timeout=30):
        return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)

    def _execute(self, inputs, context=None):
        provider = inputs.get("provider", "aws").lower()
        action = inputs.get("action", "status")

        try:
            if provider == "aws":
                if action == "s3-list":
                    bucket = inputs.get("bucket", "")
                    r = self._run(["aws", "s3", "ls", f"s3://{bucket}" if bucket else ""])
                    return AlgorithmResult("success" if r.returncode == 0 else "failure",
                        {"output": r.stdout[:3000], "bucket": bucket}, {"skill": "cloud-deploy"})

                elif action == "s3-upload":
                    file_path = inputs.get("file", "")
                    bucket = inputs.get("bucket", "")
                    key = os.path.basename(file_path)
                    r = self._run(["aws", "s3", "cp", file_path, f"s3://{bucket}/{key}"])
                    return AlgorithmResult("success" if r.returncode == 0 else "failure",
                        {"uploaded": key, "bucket": bucket}, {"skill": "cloud-deploy"})

                elif action == "ec2-list":
                    region = inputs.get("region", "us-east-1")
                    r = self._run(["aws", "ec2", "describe-instances", "--region", region,
                                   "--query", "Reservations[*].Instances[*].[InstanceId,State.Name,InstanceType]",
                                   "--output", "json"])
                    if r.returncode == 0:
                        instances = json.loads(r.stdout)
                        return AlgorithmResult("success", {"instances": instances, "region": region},
                                               {"skill": "cloud-deploy"})

                elif action == "lambda-list":
                    r = self._run(["aws", "lambda", "list-functions", "--output", "json"])
                    if r.returncode == 0:
                        data = json.loads(r.stdout)
                        funcs = [{"name": f["FunctionName"], "runtime": f.get("Runtime"),
                                  "memory": f.get("MemorySize")}
                                 for f in data.get("Functions", [])]
                        return AlgorithmResult("success", {"functions": funcs}, {"skill": "cloud-deploy"})

                elif action == "status":
                    r = self._run(["aws", "sts", "get-caller-identity"])
                    if r.returncode == 0:
                        return AlgorithmResult("success", json.loads(r.stdout), {"skill": "cloud-deploy"})

            elif provider == "gcp":
                if action == "status":
                    r = self._run(["gcloud", "config", "list", "--format=json"])
                    if r.returncode == 0:
                        return AlgorithmResult("success", json.loads(r.stdout), {"skill": "cloud-deploy"})

                elif action == "instances":
                    r = self._run(["gcloud", "compute", "instances", "list", "--format=json"])
                    if r.returncode == 0:
                        return AlgorithmResult("success", {"instances": json.loads(r.stdout)},
                                               {"skill": "cloud-deploy"})

                elif action == "deploy":
                    r = self._run(["gcloud", "app", "deploy", "--quiet"])
                    return AlgorithmResult("success" if r.returncode == 0 else "failure",
                        {"output": r.stdout[:2000]}, {"skill": "cloud-deploy"})

            elif provider == "azure":
                if action == "status":
                    r = self._run(["az", "account", "show", "-o", "json"])
                    if r.returncode == 0:
                        return AlgorithmResult("success", json.loads(r.stdout), {"skill": "cloud-deploy"})

            return AlgorithmResult("failure", None, {"error": f"Unknown {provider}/{action}"})
        except FileNotFoundError:
            return AlgorithmResult("failure", None, {"error": f"{provider} CLI not installed"})
        except Exception as e:
            return AlgorithmResult("failure", None, {"error": str(e)})
