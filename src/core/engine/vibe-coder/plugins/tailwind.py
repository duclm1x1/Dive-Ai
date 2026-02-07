from __future__ import annotations

from typing import List

from .base import GateSpec
from .common import detect_package_manager, merged_deps, read_package_json, run_script_cmd, scripts


class TailwindPlugin:
    name = 'tailwind'

    def detect(self, repo_root: str) -> bool:
        pkg = read_package_json(repo_root)
        deps = merged_deps(pkg)
        return 'tailwindcss' in deps

    def suggested_gates(self, repo_root: str) -> List[GateSpec]:
        pkg = read_package_json(repo_root)
        sc = scripts(pkg)
        pm = detect_package_manager(repo_root)

        out: List[GateSpec] = []
        # Tailwind usually rides on build, but we also support a dedicated "tw"/"tailwind" script if present.
        for s in ['build', 'tailwind', 'tw']:
            if s in sc:
                out.append(GateSpec(name=f'tailwind-{s}', cmd=run_script_cmd(pm, s)))
                break
        return out
