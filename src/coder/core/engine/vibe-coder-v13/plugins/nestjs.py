from __future__ import annotations

from typing import List

from .base import GateSpec
from .common import detect_package_manager, merged_deps, read_package_json, run_script_cmd, scripts


class NestJsPlugin:
    name = 'nestjs'

    def detect(self, repo_root: str) -> bool:
        pkg = read_package_json(repo_root)
        deps = merged_deps(pkg)
        return '@nestjs/core' in deps or '@nestjs/common' in deps

    def suggested_gates(self, repo_root: str) -> List[GateSpec]:
        pkg = read_package_json(repo_root)
        sc = scripts(pkg)
        pm = detect_package_manager(repo_root)

        out: List[GateSpec] = []
        if 'lint' in sc:
            out.append(GateSpec(name='nest-lint', cmd=run_script_cmd(pm, 'lint')))
        if 'typecheck' in sc:
            out.append(GateSpec(name='nest-typecheck', cmd=run_script_cmd(pm, 'typecheck')))
        if 'test' in sc:
            out.append(GateSpec(name='nest-test', cmd=run_script_cmd(pm, 'test')))
        if 'build' in sc:
            out.append(GateSpec(name='nest-build', cmd=run_script_cmd(pm, 'build')))
        return out
