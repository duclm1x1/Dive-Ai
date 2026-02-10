"""
📖 AUTO DOC GENERATOR
Automatically generate documentation

Based on V28's vibe_engine/auto_doc_generator.py
"""

import os
import sys
import re
from typing import Dict, Any, List
from dataclasses import dataclass
from pathlib import Path

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from core.algorithms.base_algorithm import (
    BaseAlgorithm, AlgorithmResult, AlgorithmSpec, AlgorithmIOSpec, IOField
)


@dataclass
class DocSection:
    """A documentation section"""
    title: str
    content: str
    level: int = 1


class AutoDocGeneratorAlgorithm(BaseAlgorithm):
    """
    📖 Auto Doc Generator
    
    Generates documentation:
    - API docs from code
    - README generation
    - Changelog creation
    - Usage examples
    
    From V28: vibe_engine/auto_doc_generator.py
    """
    
    def __init__(self):
        self.spec = AlgorithmSpec(
            algorithm_id="AutoDocGenerator",
            name="Auto Doc Generator",
            level="operational",
            category="documentation",
            version="1.0",
            description="Automatically generate documentation",
            io=AlgorithmIOSpec(
                inputs=[
                    IOField("action", "string", True, "generate/update"),
                    IOField("source", "string", False, "Source code/file"),
                    IOField("doc_type", "string", False, "Type of doc")
                ],
                outputs=[
                    IOField("documentation", "string", True, "Generated docs")
                ]
            ),
            steps=["Parse source", "Extract metadata", "Generate sections", "Format output"],
            tags=["documentation", "generation", "api-docs"]
        )
    
    def execute(self, params: Dict[str, Any]) -> AlgorithmResult:
        action = params.get("action", "generate")
        source = params.get("source", "")
        doc_type = params.get("doc_type", "api")
        
        print(f"\n📖 Auto Doc Generator")
        
        if action == "generate":
            if doc_type == "api":
                docs = self._generate_api_docs(source)
            elif doc_type == "readme":
                docs = self._generate_readme(params.get("project", {}))
            elif doc_type == "changelog":
                docs = self._generate_changelog(params.get("changes", []))
            else:
                docs = self._generate_generic(source)
        else:
            docs = "# Documentation\n\nNo content generated."
        
        print(f"   Generated: {doc_type} documentation")
        
        return AlgorithmResult(
            status="success",
            data={
                "documentation": docs,
                "type": doc_type,
                "lines": len(docs.split('\n'))
            }
        )
    
    def _generate_api_docs(self, source: str) -> str:
        sections = []
        
        # Parse functions
        func_pattern = r'def\s+(\w+)\s*\((.*?)\).*?:\s*(?:"""(.*?)""")?'
        functions = re.findall(func_pattern, source, re.DOTALL)
        
        if functions:
            sections.append(DocSection("Functions", "", 2))
            for func_name, params, docstring in functions:
                doc = docstring.strip() if docstring else "No documentation"
                sections.append(DocSection(
                    f"`{func_name}({params})`",
                    doc,
                    3
                ))
        
        # Parse classes
        class_pattern = r'class\s+(\w+).*?:\s*(?:"""(.*?)""")?'
        classes = re.findall(class_pattern, source, re.DOTALL)
        
        if classes:
            sections.append(DocSection("Classes", "", 2))
            for class_name, docstring in classes:
                doc = docstring.strip() if docstring else "No documentation"
                sections.append(DocSection(f"`{class_name}`", doc, 3))
        
        # Build markdown
        output = "# API Documentation\n\n"
        for section in sections:
            prefix = "#" * section.level
            output += f"{prefix} {section.title}\n\n"
            if section.content:
                output += f"{section.content}\n\n"
        
        return output
    
    def _generate_readme(self, project: Dict) -> str:
        name = project.get("name", "Project")
        description = project.get("description", "A project")
        install = project.get("install", "pip install .")
        usage = project.get("usage", "See documentation")
        
        return f'''# {name}

{description}

## Installation

```bash
{install}
```

## Usage

{usage}

## License

MIT
'''
    
    def _generate_changelog(self, changes: List[Dict]) -> str:
        output = "# Changelog\n\n"
        
        for change in changes:
            version = change.get("version", "0.0.0")
            date = change.get("date", "TBD")
            items = change.get("items", [])
            
            output += f"## [{version}] - {date}\n\n"
            for item in items:
                output += f"- {item}\n"
            output += "\n"
        
        return output
    
    def _generate_generic(self, source: str) -> str:
        return f"# Documentation\n\n```\n{source[:500]}\n```"


def register(algorithm_manager):
    algo = AutoDocGeneratorAlgorithm()
    algorithm_manager.register("AutoDocGenerator", algo)
    print("✅ AutoDocGenerator registered")


if __name__ == "__main__":
    algo = AutoDocGeneratorAlgorithm()
    result = algo.execute({
        "action": "generate",
        "doc_type": "api",
        "source": '''
def calculate(a: int, b: int) -> int:
    """Calculate the sum of two numbers."""
    return a + b

class Calculator:
    """A simple calculator class."""
    pass
'''
    })
    print(result.data["documentation"])
