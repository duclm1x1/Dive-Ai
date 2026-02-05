from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(content, encoding='utf-8')


def scaffold_nextjs(outdir: str, spec: Dict[str, Any]) -> None:
    root = Path(outdir)
    name = str(((spec.get('project') or {}).get('name') or 'next-app')).strip() or 'next-app'
    desc = str(((spec.get('project') or {}).get('description') or '')).strip()

    _write(root / 'package.json', json.dumps({
        'name': name,
        'private': True,
        'scripts': {
            'dev': 'next dev',
            'build': 'next build',
            'start': 'next start',
            'lint': 'next lint',
            'test': 'node ./scripts/smoke-test.js'
        }
    }, indent=2) + '\n')

    _write(root / 'next.config.mjs', "export default {};\n")
    _write(root / 'tsconfig.json', json.dumps({
        'compilerOptions': {
            'target': 'ES2022',
            'lib': ['dom', 'dom.iterable', 'esnext'],
            'allowJs': False,
            'skipLibCheck': True,
            'strict': True,
            'noEmit': True,
            'module': 'esnext',
            'moduleResolution': 'bundler',
            'resolveJsonModule': True,
            'isolatedModules': True,
            'jsx': 'preserve'
        },
        'include': ['next-env.d.ts', '**/*.ts', '**/*.tsx'],
        'exclude': ['node_modules']
    }, indent=2) + '\n')

    _write(root / 'app' / 'layout.tsx', f"""export default function RootLayout({{ children }}: {{ children: React.ReactNode }}) {{
  return (
    <html lang=\"en\">
      <body style={{{{ fontFamily: 'system-ui', margin: 0 }}}}>{{children}}</body>
    </html>
  );
}}
""")

    _write(root / 'app' / 'page.tsx', f"""export default function Page() {{
  return (
    <main style={{{{ padding: 24 }}}}>
      <h1>{name}</h1>
      <p>{desc or 'Scaffolded by Vibe Coder v12.2'}</p>
    </main>
  );
}}
""")

    _write(root / 'scripts' / 'smoke-test.js', """// Minimal smoke test runner (no deps)
const fs = require('fs');
const path = require('path');

const required = [
  'app/page.tsx',
  'app/layout.tsx',
  'package.json',
];

let ok = true;
for (const rel of required) {
  const p = path.join(process.cwd(), rel);
  if (!fs.existsSync(p)) {
    console.error('Missing', rel);
    ok = false;
  }
}
process.exit(ok ? 0 : 1);
""")

    _write(root / 'README.md', f"""# {name}

{desc}

## Dev

```bash
npm install
npm run dev
```
""")


def scaffold_nestjs(outdir: str, spec: Dict[str, Any]) -> None:
    root = Path(outdir)
    name = str(((spec.get('project') or {}).get('name') or 'nest-service')).strip() or 'nest-service'
    desc = str(((spec.get('project') or {}).get('description') or '')).strip()

    _write(root / 'package.json', json.dumps({
        'name': name,
        'private': True,
        'scripts': {
            'start': 'node dist/main.js',
            'start:dev': 'node src/main.ts',
            'build': 'echo "Scaffold only"',
            'lint': 'echo "Add eslint"',
            'test': 'echo "Add jest"'
        }
    }, indent=2) + '\n')

    _write(root / 'src' / 'main.ts', """import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);
  await app.listen(process.env.PORT || 3000);
}
bootstrap();
""")

    _write(root / 'src' / 'app.module.ts', """import { Module } from '@nestjs/common';
import { AppController } from './app.controller';
import { AppService } from './app.service';

@Module({
  imports: [],
  controllers: [AppController],
  providers: [AppService],
})
export class AppModule {}
""")

    _write(root / 'src' / 'app.controller.ts', """import { Controller, Get } from '@nestjs/common';
import { AppService } from './app.service';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Get('/health')
  health() {
    return { status: 'ok' };
  }
}
""")

    _write(root / 'src' / 'app.service.ts', """import { Injectable } from '@nestjs/common';

@Injectable()
export class AppService {}
""")

    _write(root / 'README.md', f"""# {name}

{desc}

## Next steps
- Add DTO validation (class-validator)
- Add OpenAPI (Swagger)
- Add tests + lint + build pipeline
""")


def scaffold_website_or_tailwind(outdir: str, spec: Dict[str, Any]) -> None:
    root = Path(outdir)
    name = str(((spec.get('project') or {}).get('name') or 'website')).strip() or 'website'
    desc = str(((spec.get('project') or {}).get('description') or '')).strip()

    _write(root / 'index.html', f"""<!doctype html>
<html lang=\"en\">
  <head>
    <meta charset=\"utf-8\" />
    <meta name=\"viewport\" content=\"width=device-width,initial-scale=1\" />
    <title>{name}</title>
    <meta name=\"description\" content=\"{desc}\" />
  </head>
  <body>
    <main style=\"font-family:system-ui;padding:24px\">
      <h1>{name}</h1>
      <p>{desc or 'Scaffolded by Vibe Coder v12.2'}</p>
    </main>
  </body>
</html>
""")

    _write(root / 'README.md', f"""# {name}

{desc}

This is a minimal static scaffold. Add Tailwind/Vite/Next based on your stack.
""")


def scaffold_n8n(outdir: str, spec: Dict[str, Any]) -> None:
    root = Path(outdir)
    name = str(((spec.get('project') or {}).get('name') or 'n8n-workflow')).strip() or 'n8n-workflow'

    workflow = {
        'name': name,
        'nodes': [
            {
                'parameters': {},
                'id': '1',
                'name': 'Webhook',
                'type': 'n8n-nodes-base.webhook',
                'typeVersion': 1,
                'position': [250, 300],
            },
            {
                'parameters': {
                    'url': 'https://example.com',
                    'options': {
                        'timeout': 30000,
                        'retry': {
                            'maxRetries': 3,
                        }
                    }
                },
                'id': '2',
                'name': 'HTTP Request',
                'type': 'n8n-nodes-base.httpRequest',
                'typeVersion': 4,
                'position': [500, 300],
            }
        ],
        'connections': {
            'Webhook': {
                'main': [[{'node': 'HTTP Request', 'type': 'main', 'index': 0}]]
            }
        },
        'settings': {
            'errorWorkflow': '<ERROR_WORKFLOW_ID_PLACEHOLDER>'
        }
    }

    _write(root / f'{name}.n8n.json', json.dumps(workflow, indent=2, ensure_ascii=False) + '\n')
    _write(root / 'README.md', """# n8n workflow scaffold

- Replace placeholders (error workflow id, env vars)
- Do not commit credential ids/names
""")


def scaffold(kind: str, outdir: str, spec: Dict[str, Any]) -> None:
    if kind == 'nextjs':
        return scaffold_nextjs(outdir, spec)
    if kind == 'nestjs':
        return scaffold_nestjs(outdir, spec)
    if kind in {'tailwind', 'website'}:
        return scaffold_website_or_tailwind(outdir, spec)
    if kind == 'n8n':
        return scaffold_n8n(outdir, spec)
    raise ValueError(f'Unknown kind: {kind}')
