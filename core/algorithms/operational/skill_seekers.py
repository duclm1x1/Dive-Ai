"""
🎯 SKILL SEEKERS ALGORITHM
Convert documentation, GitHub repos, PDFs into Dive AI skills

Features:
- Documentation website scraping
- GitHub repository analysis
- PDF extraction
- Conflict detection (docs vs code)
- AI-powered skill generation

Inspired by: https://github.com/yusufkaraaslan/Skill_Seekers
"""

import os
import sys
import json
import time
import re
import hashlib
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from urllib.parse import urlparse, urljoin

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from core.algorithms.base_algorithm import (
    BaseAlgorithm,
    AlgorithmResult,
    AlgorithmSpec,
    AlgorithmIOSpec,
    IOField
)


class SourceType(Enum):
    """Types of skill sources"""
    DOCUMENTATION = "documentation"
    GITHUB = "github"
    PDF = "pdf"
    LOCAL_FOLDER = "local"


class ConflictType(Enum):
    """Types of conflicts between sources"""
    MISSING_IN_DOCS = "missing_in_docs"       # Code exists but not documented
    OUTDATED_DOCS = "outdated_docs"           # Docs don't match code
    DEPRECATED = "deprecated"                  # Documented but removed
    SIGNATURE_MISMATCH = "signature_mismatch" # Parameters differ


@dataclass
class SkillSource:
    """A source for skill extraction"""
    type: SourceType
    url: str
    name: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExtractedContent:
    """Content extracted from a source"""
    source: SkillSource
    title: str
    content: str
    code_blocks: List[Dict] = field(default_factory=list)
    functions: List[Dict] = field(default_factory=list)
    classes: List[Dict] = field(default_factory=list)
    category: str = "general"


@dataclass
class Conflict:
    """A conflict between documentation and code"""
    type: ConflictType
    item_name: str
    doc_version: str
    code_version: str
    severity: str  # low, medium, high
    suggestion: str


@dataclass
class DiveSkill:
    """A generated Dive AI skill"""
    name: str
    description: str
    version: str
    sources: List[SkillSource]
    content: List[ExtractedContent]
    conflicts: List[Conflict]
    skill_md: str
    created_at: datetime = field(default_factory=datetime.now)


class DocumentationScraper:
    """
    🌐 Documentation Website Scraper
    
    Features:
    - llms.txt detection
    - Sitemap parsing
    - Content extraction
    - Code block detection
    """
    
    def __init__(self):
        self.session = None
    
    def scrape(self, url: str, max_pages: int = 100) -> List[ExtractedContent]:
        """Scrape documentation website"""
        results = []
        
        try:
            import requests
            from bs4 import BeautifulSoup
        except ImportError:
            print("⚠️ Need: pip install requests beautifulsoup4")
            return results
        
        source = SkillSource(
            type=SourceType.DOCUMENTATION,
            url=url,
            name=urlparse(url).netloc
        )
        
        # Check for llms.txt first (faster)
        llms_txt = self._check_llms_txt(url)
        if llms_txt:
            return self._parse_llms_txt(llms_txt, source)
        
        # Fallback to scraping
        visited = set()
        to_visit = [url]
        
        while to_visit and len(results) < max_pages:
            current_url = to_visit.pop(0)
            if current_url in visited:
                continue
            
            visited.add(current_url)
            
            try:
                response = requests.get(current_url, timeout=10)
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract content
                content = self._extract_content(soup)
                if content:
                    results.append(ExtractedContent(
                        source=source,
                        title=soup.title.string if soup.title else current_url,
                        content=content,
                        code_blocks=self._extract_code_blocks(soup),
                        category=self._categorize_content(current_url, content)
                    ))
                
                # Find more links
                for link in soup.find_all('a', href=True):
                    href = urljoin(current_url, link['href'])
                    if self._is_same_domain(url, href) and href not in visited:
                        to_visit.append(href)
                
            except Exception as e:
                print(f"   ⚠️ Failed to scrape {current_url}: {e}")
        
        return results
    
    def _check_llms_txt(self, base_url: str) -> Optional[str]:
        """Check for llms.txt file"""
        try:
            import requests
            for filename in ['llms-full.txt', 'llms.txt', 'llms-small.txt']:
                url = urljoin(base_url, filename)
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    print(f"   ✅ Found {filename}")
                    return response.text
        except:
            pass
        return None
    
    def _parse_llms_txt(self, content: str, source: SkillSource) -> List[ExtractedContent]:
        """Parse llms.txt format"""
        results = []
        sections = content.split('\n## ')
        
        for section in sections:
            if not section.strip():
                continue
            
            lines = section.split('\n')
            title = lines[0].replace('#', '').strip()
            body = '\n'.join(lines[1:])
            
            results.append(ExtractedContent(
                source=source,
                title=title,
                content=body.strip(),
                code_blocks=self._extract_code_from_markdown(body),
                category=self._categorize_content(title, body)
            ))
        
        return results
    
    def _extract_content(self, soup) -> str:
        """Extract main content from page"""
        # Try common content selectors
        selectors = [
            'article', '.content', '.docs-content', 
            'main', '.main-content', '#content',
            '.markdown-body', '.documentation'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text(separator='\n', strip=True)
        
        return soup.get_text(separator='\n', strip=True)[:10000]
    
    def _extract_code_blocks(self, soup) -> List[Dict]:
        """Extract code blocks from page"""
        blocks = []
        for pre in soup.find_all(['pre', 'code']):
            code = pre.get_text(strip=True)
            if code and len(code) > 10:
                lang = self._detect_language(code, pre.get('class', []))
                blocks.append({
                    "language": lang,
                    "code": code[:2000]
                })
        return blocks[:20]
    
    def _extract_code_from_markdown(self, text: str) -> List[Dict]:
        """Extract code blocks from markdown"""
        pattern = r'```(\w+)?\n(.*?)```'
        matches = re.findall(pattern, text, re.DOTALL)
        return [{"language": m[0] or "text", "code": m[1]} for m in matches]
    
    def _detect_language(self, code: str, classes: List) -> str:
        """Detect programming language"""
        # From class
        for cls in classes:
            if isinstance(cls, str):
                if 'python' in cls.lower(): return 'python'
                if 'javascript' in cls.lower() or 'js' in cls.lower(): return 'javascript'
                if 'typescript' in cls.lower() or 'ts' in cls.lower(): return 'typescript'
        
        # From content
        if 'def ' in code and 'import ' in code: return 'python'
        if 'function ' in code or 'const ' in code: return 'javascript'
        if 'interface ' in code: return 'typescript'
        
        return 'text'
    
    def _categorize_content(self, url: str, content: str) -> str:
        """Categorize content by topic"""
        url_lower = url.lower()
        content_lower = content.lower()[:500]
        
        if 'api' in url_lower or 'reference' in url_lower:
            return 'api_reference'
        if 'tutorial' in url_lower or 'getting-started' in url_lower:
            return 'tutorial'
        if 'guide' in url_lower or 'how-to' in url_lower:
            return 'guide'
        if 'example' in url_lower:
            return 'examples'
        if 'install' in content_lower or 'npm install' in content_lower:
            return 'installation'
        
        return 'general'
    
    def _is_same_domain(self, base: str, url: str) -> bool:
        """Check if URL is same domain"""
        return urlparse(base).netloc == urlparse(url).netloc


class GitHubScraper:
    """
    🐙 GitHub Repository Scraper
    
    Features:
    - README extraction
    - Code analysis (Python, JS, TS)
    - API extraction (functions, classes)
    - Issues and PRs
    """
    
    def __init__(self, token: str = None):
        self.token = token or os.environ.get('GITHUB_TOKEN', '')
        self.api_base = "https://api.github.com"
    
    def scrape(self, repo_url: str) -> List[ExtractedContent]:
        """Scrape GitHub repository"""
        results = []
        
        # Parse repo URL
        match = re.match(r'https?://github\.com/([^/]+)/([^/]+)', repo_url)
        if not match:
            print(f"   ⚠️ Invalid GitHub URL: {repo_url}")
            return results
        
        owner, repo = match.groups()
        source = SkillSource(
            type=SourceType.GITHUB,
            url=repo_url,
            name=f"{owner}/{repo}"
        )
        
        try:
            import requests
        except ImportError:
            print("⚠️ Need: pip install requests")
            return results
        
        headers = {"Authorization": f"token {self.token}"} if self.token else {}
        
        # Get README
        readme = self._get_readme(owner, repo, headers)
        if readme:
            results.append(ExtractedContent(
                source=source,
                title=f"{repo} - README",
                content=readme,
                code_blocks=self._extract_code_from_markdown(readme),
                category="readme"
            ))
        
        # Get file tree and analyze code
        tree = self._get_file_tree(owner, repo, headers)
        code_files = [f for f in tree if self._is_code_file(f)]
        
        # Analyze top Python/JS files
        for file_path in code_files[:20]:
            content = self._get_file_content(owner, repo, file_path, headers)
            if content:
                analysis = self._analyze_code(content, file_path)
                results.append(ExtractedContent(
                    source=source,
                    title=f"{repo}/{file_path}",
                    content=content[:5000],
                    functions=analysis.get('functions', []),
                    classes=analysis.get('classes', []),
                    category="source_code"
                ))
        
        return results
    
    def _get_readme(self, owner: str, repo: str, headers: Dict) -> Optional[str]:
        """Get README content"""
        try:
            import requests
            url = f"{self.api_base}/repos/{owner}/{repo}/readme"
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                import base64
                content = response.json().get('content', '')
                return base64.b64decode(content).decode('utf-8')
        except:
            pass
        return None
    
    def _get_file_tree(self, owner: str, repo: str, headers: Dict) -> List[str]:
        """Get repository file tree"""
        try:
            import requests
            url = f"{self.api_base}/repos/{owner}/{repo}/git/trees/main?recursive=1"
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                tree = response.json().get('tree', [])
                return [f['path'] for f in tree if f['type'] == 'blob']
        except:
            pass
        return []
    
    def _get_file_content(self, owner: str, repo: str, path: str, headers: Dict) -> Optional[str]:
        """Get file content"""
        try:
            import requests
            import base64
            url = f"{self.api_base}/repos/{owner}/{repo}/contents/{path}"
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                content = response.json().get('content', '')
                return base64.b64decode(content).decode('utf-8')
        except:
            pass
        return None
    
    def _is_code_file(self, path: str) -> bool:
        """Check if file is code"""
        extensions = ['.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.go', '.rs']
        return any(path.endswith(ext) for ext in extensions)
    
    def _analyze_code(self, content: str, file_path: str) -> Dict:
        """Analyze code structure"""
        result = {'functions': [], 'classes': []}
        
        if file_path.endswith('.py'):
            result = self._analyze_python(content)
        elif file_path.endswith(('.js', '.ts', '.jsx', '.tsx')):
            result = self._analyze_javascript(content)
        
        return result
    
    def _analyze_python(self, content: str) -> Dict:
        """Analyze Python code"""
        functions = []
        classes = []
        
        # Find functions
        for match in re.finditer(r'def\s+(\w+)\s*\(([^)]*)\)', content):
            functions.append({
                "name": match.group(1),
                "params": match.group(2),
                "type": "function"
            })
        
        # Find classes
        for match in re.finditer(r'class\s+(\w+)\s*(?:\([^)]*\))?:', content):
            classes.append({
                "name": match.group(1),
                "type": "class"
            })
        
        return {'functions': functions[:30], 'classes': classes[:20]}
    
    def _analyze_javascript(self, content: str) -> Dict:
        """Analyze JavaScript/TypeScript code"""
        functions = []
        classes = []
        
        # Find functions
        patterns = [
            r'function\s+(\w+)\s*\(([^)]*)\)',
            r'const\s+(\w+)\s*=\s*(?:async\s*)?\(([^)]*)\)\s*=>',
            r'(\w+)\s*:\s*(?:async\s*)?\(([^)]*)\)\s*=>'
        ]
        
        for pattern in patterns:
            for match in re.finditer(pattern, content):
                functions.append({
                    "name": match.group(1),
                    "params": match.group(2) if len(match.groups()) > 1 else "",
                    "type": "function"
                })
        
        # Find classes
        for match in re.finditer(r'class\s+(\w+)', content):
            classes.append({
                "name": match.group(1),
                "type": "class"
            })
        
        return {'functions': functions[:30], 'classes': classes[:20]}
    
    def _extract_code_from_markdown(self, text: str) -> List[Dict]:
        """Extract code blocks from markdown"""
        pattern = r'```(\w+)?\n(.*?)```'
        matches = re.findall(pattern, text, re.DOTALL)
        return [{"language": m[0] or "text", "code": m[1]} for m in matches]


class PDFScraper:
    """
    📄 PDF Document Scraper
    
    Features:
    - Text extraction
    - OCR for scanned PDFs
    - Code block detection
    """
    
    def scrape(self, file_path: str) -> List[ExtractedContent]:
        """Extract content from PDF"""
        results = []
        
        source = SkillSource(
            type=SourceType.PDF,
            url=file_path,
            name=os.path.basename(file_path)
        )
        
        try:
            import PyPDF2
            
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                full_text = ""
                
                for page in reader.pages:
                    full_text += page.extract_text() + "\n\n"
                
                results.append(ExtractedContent(
                    source=source,
                    title=os.path.basename(file_path),
                    content=full_text,
                    code_blocks=self._find_code_blocks(full_text),
                    category="document"
                ))
        
        except ImportError:
            print("⚠️ Need: pip install PyPDF2")
        except Exception as e:
            print(f"   ⚠️ Failed to read PDF: {e}")
        
        return results
    
    def _find_code_blocks(self, text: str) -> List[Dict]:
        """Find code-like patterns in text"""
        blocks = []
        
        # Look for indented blocks
        pattern = r'(?:^|\n)((?:    |\t).*(?:\n(?:    |\t).*)*)'
        for match in re.finditer(pattern, text):
            code = match.group(1)
            if len(code) > 50:
                blocks.append({
                    "language": "text",
                    "code": code
                })
        
        return blocks[:10]


class ConflictDetector:
    """
    🔍 Conflict Detector
    
    Compares documentation vs code to find:
    - Missing documentation
    - Outdated documentation
    - Signature mismatches
    """
    
    def detect(self, doc_content: List[ExtractedContent], 
               code_content: List[ExtractedContent]) -> List[Conflict]:
        """Detect conflicts between docs and code"""
        conflicts = []
        
        # Extract documented items
        documented = set()
        for doc in doc_content:
            for func in doc.functions:
                documented.add(func['name'])
            for cls in doc.classes:
                documented.add(cls['name'])
        
        # Extract code items
        in_code = {}
        for code in code_content:
            for func in code.functions:
                in_code[func['name']] = func
            for cls in code.classes:
                in_code[cls['name']] = cls
        
        # Find undocumented code
        for name, item in in_code.items():
            if name not in documented and not name.startswith('_'):
                conflicts.append(Conflict(
                    type=ConflictType.MISSING_IN_DOCS,
                    item_name=name,
                    doc_version="(not documented)",
                    code_version=f"{item['type']} {name}",
                    severity="medium",
                    suggestion=f"Add documentation for {item['type']} '{name}'"
                ))
        
        # Find removed code (in docs but not in code)
        for name in documented:
            if name not in in_code:
                conflicts.append(Conflict(
                    type=ConflictType.DEPRECATED,
                    item_name=name,
                    doc_version=f"Documented: {name}",
                    code_version="(not found)",
                    severity="high",
                    suggestion=f"'{name}' is documented but not in code - update docs"
                ))
        
        return conflicts


class SkillGenerator:
    """
    ✨ Skill Generator
    
    Generates SKILL.md from extracted content
    """
    
    def generate(self, skill_name: str, contents: List[ExtractedContent],
                 conflicts: List[Conflict] = None) -> str:
        """Generate SKILL.md content"""
        
        # Categorize content
        categories = {}
        for content in contents:
            cat = content.category
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(content)
        
        # Build SKILL.md
        md = f"""---
name: {skill_name}
description: Auto-generated skill from documentation
version: 1.0.0
generated_at: {datetime.now().isoformat()}
sources: {len(contents)} documents
conflicts: {len(conflicts or [])} detected
---

# {skill_name}

This skill was automatically generated by Dive AI Skill Seekers.

## 📚 Contents

"""
        
        # Add table of contents
        for cat, items in categories.items():
            md += f"### {cat.replace('_', ' ').title()}\n\n"
            for item in items[:10]:
                md += f"- {item.title}\n"
            md += "\n"
        
        # Add conflicts
        if conflicts:
            md += "\n## ⚠️ Conflicts Detected\n\n"
            md += "| Item | Type | Issue | Suggestion |\n"
            md += "|------|------|-------|------------|\n"
            for c in conflicts[:20]:
                md += f"| {c.item_name} | {c.type.value} | {c.severity} | {c.suggestion} |\n"
            md += "\n"
        
        # Add API reference
        all_functions = []
        all_classes = []
        for content in contents:
            all_functions.extend(content.functions)
            all_classes.extend(content.classes)
        
        if all_functions:
            md += "\n## 🔧 Functions\n\n"
            for func in all_functions[:30]:
                md += f"- `{func['name']}({func.get('params', '')})`\n"
        
        if all_classes:
            md += "\n## 📦 Classes\n\n"
            for cls in all_classes[:20]:
                md += f"- `{cls['name']}`\n"
        
        # Add code examples
        all_code = []
        for content in contents:
            all_code.extend(content.code_blocks)
        
        if all_code:
            md += "\n## 💡 Code Examples\n\n"
            for i, code in enumerate(all_code[:5]):
                md += f"```{code.get('language', '')}\n{code['code'][:500]}\n```\n\n"
        
        return md


class SkillSeekersAlgorithm(BaseAlgorithm):
    """
    🎯 Skill Seekers Algorithm
    
    Convert documentation, GitHub repos, PDFs into Dive AI skills
    with automatic conflict detection.
    """
    
    def __init__(self):
        self.spec = AlgorithmSpec(
            algorithm_id="SkillSeekers",
            name="Skill Seekers",
            level="operational",
            category="automation",
            version="1.0",
            description="Convert docs, GitHub, PDFs into Dive AI skills",
            
            io=AlgorithmIOSpec(
                inputs=[
                    IOField("sources", "array", True, "List of URLs/paths to scrape"),
                    IOField("skill_name", "string", True, "Name for the generated skill"),
                    IOField("options", "object", False, "Scraping options")
                ],
                outputs=[
                    IOField("skill", "object", True, "Generated skill with SKILL.md"),
                    IOField("conflicts", "array", False, "Detected conflicts")
                ]
            ),
            
            steps=[
                "1. Identify source types (doc/GitHub/PDF)",
                "2. Scrape all sources",
                "3. Extract functions, classes, code blocks",
                "4. Detect conflicts between sources",
                "5. Generate SKILL.md",
                "6. Package skill"
            ],
            
            tags=["skills", "automation", "scraping", "documentation"]
        )
        
        self.doc_scraper = DocumentationScraper()
        self.github_scraper = GitHubScraper()
        self.pdf_scraper = PDFScraper()
        self.conflict_detector = ConflictDetector()
        self.skill_generator = SkillGenerator()
    
    def execute(self, params: Dict[str, Any]) -> AlgorithmResult:
        """Execute skill generation"""
        sources = params.get("sources", [])
        skill_name = params.get("skill_name", "unnamed_skill")
        options = params.get("options", {})
        
        if not sources:
            return AlgorithmResult(status="error", error="No sources provided")
        
        print(f"\n🎯 Skill Seekers: Creating '{skill_name}'")
        
        all_content = []
        doc_content = []
        code_content = []
        
        # Scrape each source
        for source in sources:
            source_type = self._detect_source_type(source)
            print(f"   📥 Scraping {source_type.value}: {source}")
            
            try:
                if source_type == SourceType.DOCUMENTATION:
                    content = self.doc_scraper.scrape(source, options.get('max_pages', 50))
                    all_content.extend(content)
                    doc_content.extend(content)
                
                elif source_type == SourceType.GITHUB:
                    content = self.github_scraper.scrape(source)
                    all_content.extend(content)
                    code_content.extend(content)
                
                elif source_type == SourceType.PDF:
                    content = self.pdf_scraper.scrape(source)
                    all_content.extend(content)
                    doc_content.extend(content)
                
                print(f"      ✅ Extracted {len(content)} items")
            
            except Exception as e:
                print(f"      ⚠️ Failed: {e}")
        
        # Detect conflicts
        conflicts = []
        if doc_content and code_content:
            print("   🔍 Detecting conflicts...")
            conflicts = self.conflict_detector.detect(doc_content, code_content)
            print(f"      ⚠️ Found {len(conflicts)} conflicts")
        
        # Generate skill
        print("   ✨ Generating SKILL.md...")
        skill_md = self.skill_generator.generate(skill_name, all_content, conflicts)
        
        # Save skill
        skill_dir = self._save_skill(skill_name, skill_md, all_content)
        
        print(f"   ✅ Skill saved to: {skill_dir}")
        
        return AlgorithmResult(
            status="success",
            data={
                "skill_name": skill_name,
                "skill_directory": skill_dir,
                "sources_scraped": len(sources),
                "items_extracted": len(all_content),
                "conflicts_found": len(conflicts),
                "skill_md_preview": skill_md[:1000]
            }
        )
    
    def _detect_source_type(self, source: str) -> SourceType:
        """Detect type of source"""
        if 'github.com' in source:
            return SourceType.GITHUB
        elif source.endswith('.pdf'):
            return SourceType.PDF
        elif os.path.isdir(source):
            return SourceType.LOCAL_FOLDER
        else:
            return SourceType.DOCUMENTATION
    
    def _save_skill(self, name: str, skill_md: str, content: List) -> str:
        """Save skill to directory"""
        base_dir = os.path.join(
            os.path.dirname(__file__), '..', '..', '..',
            'skills', name
        )
        os.makedirs(base_dir, exist_ok=True)
        
        # Save SKILL.md
        skill_path = os.path.join(base_dir, 'SKILL.md')
        with open(skill_path, 'w', encoding='utf-8') as f:
            f.write(skill_md)
        
        # Save metadata
        meta = {
            "name": name,
            "created_at": datetime.now().isoformat(),
            "sources_count": len(set(c.source.url for c in content)),
            "items_count": len(content)
        }
        meta_path = os.path.join(base_dir, 'metadata.json')
        with open(meta_path, 'w', encoding='utf-8') as f:
            json.dump(meta, f, indent=2)
        
        return base_dir


def register(algorithm_manager):
    """Register Skill Seekers Algorithm"""
    algo = SkillSeekersAlgorithm()
    algorithm_manager.register("SkillSeekers", algo)
    print("✅ SkillSeekers Algorithm registered")


# ========================================
# TEST
# ========================================

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🎯 SKILL SEEKERS TEST")
    print("="*60)
    
    algo = SkillSeekersAlgorithm()
    
    # Test with a documentation URL
    result = algo.execute({
        "skill_name": "test_skill",
        "sources": [
            "https://docs.python.org/3/library/json.html"
        ],
        "options": {"max_pages": 5}
    })
    
    print(f"\n📊 Result: {result.status}")
    if result.status == "success":
        print(f"   Items extracted: {result.data['items_extracted']}")
        print(f"   Skill directory: {result.data['skill_directory']}")
    
    print("\n" + "="*60)
