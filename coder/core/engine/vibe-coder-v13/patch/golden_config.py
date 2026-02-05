from __future__ import annotations

import difflib
from dataclasses import dataclass
from pathlib import Path
from typing import List

from .autopatch import Patch


def _unified_diff(path: Path, old: str, new: str) -> str:
    return ''.join(difflib.unified_diff(
        old.splitlines(keepends=True),
        new.splitlines(keepends=True),
        fromfile=str(path),
        tofile=str(path),
    ))


def _write_if_missing(repo_root: str, rel: str, content: str) -> Patch | None:
    p = Path(repo_root) / rel
    if p.exists():
        return None
    diff = _unified_diff(p, '', content)
    return Patch(file=str(p), description=f'Golden config scaffold: create {rel}', diff=diff, applied=False)


def generate_golden_config_patches(repo_root: str, stacks: List[str]) -> List[Patch]:
    """Create-only scaffolds. Never overwrite existing files.

    This is intentionally conservative for enterprise repos.
    """

    patches: List[Patch] = []

    # Baseline editor hygiene
    editorconfig = """root = true

[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true

[*.md]
trim_trailing_whitespace = false
"""
    p = _write_if_missing(repo_root, '.editorconfig', editorconfig)
    if p:
        patches.append(p)

    vibeignore = """# Vibe Coder ignore patterns
.vibe/
node_modules/
dist/
build/
.next/
coverage/
*.min.js
*.min.css
"""
    p = _write_if_missing(repo_root, '.vibeignore', vibeignore)
    if p:
        patches.append(p)

    # TypeScript baseline
    if any(s in stacks for s in ['nextjs', 'react', 'nestjs', 'tailwind']):
        tsconfig = """{
  \"compilerOptions\": {
    \"target\": \"ES2022\",
    \"lib\": [\"dom\", \"dom.iterable\", \"es2022\"],
    \"module\": \"ESNext\",
    \"moduleResolution\": \"Bundler\",
    \"jsx\": \"preserve\",
    \"strict\": true,
    \"noEmit\": true,
    \"skipLibCheck\": true,
    \"forceConsistentCasingInFileNames\": true
  }
}
"""
        p = _write_if_missing(repo_root, 'tsconfig.json', tsconfig)
        if p:
            patches.append(p)

    # Tailwind baseline
    if 'tailwind' in stacks:
        tailwind = """import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}'
  ],
  theme: { extend: {} },
  plugins: []
}

export default config
"""
        p = _write_if_missing(repo_root, 'tailwind.config.ts', tailwind)
        if p:
            patches.append(p)

        postcss = """module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {}
  }
}
"""
        p = _write_if_missing(repo_root, 'postcss.config.js', postcss)
        if p:
            patches.append(p)

    return patches


def apply_golden_patches(patches: List[Patch]) -> List[Patch]:
    for patch in patches:
        p = Path(patch.file)
        if p.exists():
            patch.applied = False
            continue
        try:
            p.parent.mkdir(parents=True, exist_ok=True)
            # The diff already includes full content; write it directly by stripping headers.
            # Safer: reconstruct from unified diff for the create-only case.
            new_lines = []
            for ln in patch.diff.splitlines(True):
                if ln.startswith('+++') or ln.startswith('---') or ln.startswith('@@'):
                    continue
                if ln.startswith('+'):
                    new_lines.append(ln[1:])
            p.write_text(''.join(new_lines), encoding='utf-8')
            patch.applied = True
        except Exception:
            patch.applied = False
    return patches
