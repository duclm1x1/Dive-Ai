"""Compression Skill — zip, tar, gzip operations."""
import os, zipfile, tarfile, gzip, shutil, time
from ..base_skill import BaseSkill
from ...algorithms.base import AlgorithmResult
from ..skill_spec import SkillSpec, SkillCategory

class CompressionSkill(BaseSkill):
    def _build_spec(self):
        return SkillSpec(name="compression", description="Compress/decompress: zip, tar, gzip, 7z",
            category=SkillCategory.SYSTEM, version="1.0.0",
            input_schema={"action": {"type": "string", "required": True}, "source": {"type": "string", "required": True},
                          "output": {"type": "string"}, "format": {"type": "string"}},
            output_schema={"output_path": "string", "size": "integer", "files": "list"},
            tags=["zip", "tar", "gzip", "compress", "decompress", "archive", "extract"],
            trigger_patterns=[r"zip\s+", r"unzip", r"compress", r"extract\s+", r"tar\s+", r"archive"],
            combo_compatible=["file-manager", "email-send", "cloud-deploy"],
            combo_position="middle")

    def _execute(self, inputs, context=None):
        action = inputs.get("action", "compress")
        source = inputs.get("source", "")
        fmt = inputs.get("format", "zip")
        output = inputs.get("output", "")

        try:
            if action == "compress":
                if not output:
                    output = f"{source}.{fmt}" if not os.path.isdir(source) else f"{os.path.basename(source)}_{int(time.time())}.{fmt}"

                if fmt == "zip":
                    with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as zf:
                        if os.path.isdir(source):
                            for root, dirs, files in os.walk(source):
                                for f in files:
                                    fp = os.path.join(root, f)
                                    zf.write(fp, os.path.relpath(fp, source))
                        else:
                            zf.write(source, os.path.basename(source))

                elif fmt in ("tar", "tar.gz", "tgz"):
                    mode = "w:gz" if fmt in ("tar.gz", "tgz") else "w"
                    with tarfile.open(output, mode) as tf:
                        tf.add(source, arcname=os.path.basename(source))

                elif fmt == "gz":
                    if not output.endswith(".gz"):
                        output += ".gz"
                    with open(source, 'rb') as f_in:
                        with gzip.open(output, 'wb') as f_out:
                            shutil.copyfileobj(f_in, f_out)

                size = os.path.getsize(output)
                orig = sum(os.path.getsize(os.path.join(r, f)) for r, _, fs in os.walk(source) for f in fs) if os.path.isdir(source) else os.path.getsize(source)
                ratio = round((1 - size / orig) * 100, 1) if orig > 0 else 0

                return AlgorithmResult("success", {
                    "output_path": output, "size": size, "original_size": orig,
                    "ratio": f"{ratio}%", "format": fmt,
                }, {"skill": "compression"})

            elif action == "extract":
                if not output:
                    output = os.path.splitext(source)[0]
                    if output.endswith(".tar"):
                        output = output[:-4]
                os.makedirs(output, exist_ok=True)

                if source.endswith(".zip"):
                    with zipfile.ZipFile(source, 'r') as zf:
                        zf.extractall(output)
                        files = zf.namelist()
                elif source.endswith((".tar", ".tar.gz", ".tgz")):
                    with tarfile.open(source, 'r:*') as tf:
                        tf.extractall(output)
                        files = tf.getnames()
                elif source.endswith(".gz"):
                    out_file = os.path.join(output, os.path.basename(source)[:-3])
                    with gzip.open(source, 'rb') as f_in:
                        with open(out_file, 'wb') as f_out:
                            shutil.copyfileobj(f_in, f_out)
                    files = [out_file]
                else:
                    return AlgorithmResult("failure", None, {"error": "Unsupported format"})

                return AlgorithmResult("success", {
                    "output_path": output, "files": files[:50], "total_files": len(files),
                }, {"skill": "compression"})

            elif action == "list":
                files = []
                if source.endswith(".zip"):
                    with zipfile.ZipFile(source, 'r') as zf:
                        files = [{"name": i.filename, "size": i.file_size, "compressed": i.compress_size}
                                 for i in zf.infolist()[:50]]
                elif source.endswith((".tar", ".tar.gz", ".tgz")):
                    with tarfile.open(source, 'r:*') as tf:
                        files = [{"name": m.name, "size": m.size} for m in tf.getmembers()[:50]]
                return AlgorithmResult("success", {"files": files, "total": len(files)}, {"skill": "compression"})

            return AlgorithmResult("failure", None, {"error": "action: compress/extract/list"})
        except Exception as e:
            return AlgorithmResult("failure", None, {"error": str(e)})
