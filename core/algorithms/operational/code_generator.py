"""
Code Generator Algorithm
Generate code from natural language requirements

Algorithm = CODE + STEPS
"""

import os
import sys
from typing import Dict, Any

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from core.algorithms.base_algorithm import (
    BaseAlgorithm,
    AlgorithmResult,
    AlgorithmSpec,
    AlgorithmIOSpec,
    IOField
)


class CodeGeneratorAlgorithm(BaseAlgorithm):
    """
    Code Generator - Create code from requirements
    
    Uses LLM with specialized prompting for code generation
    """
    
    def __init__(self):
        self.spec = AlgorithmSpec(
            algorithm_id="CodeGenerator",
            name="Code Generator",
            level="operational",
            category="code-generation",
            version="1.0",
            description="Generate code from natural language requirements using LLM with code-specialized prompting.",
            
            io=AlgorithmIOSpec(
                inputs=[
                    IOField("requirements", "string", True, "What to code"),
                    IOField("language", "string", False, "Programming language (default: python)"),
                    IOField("context", "string", False, "Codebase context"),
                    IOField("style", "string", False, "Code style (clean/performant/minimal)")
                ],
                outputs=[
                    IOField("code", "string", True, "Generated code"),
                    IOField("explanation", "string", True, "Code explanation"),
                    IOField("dependencies", "list", False, "Required dependencies")
                ]
            ),
            
            steps=[
                "Step 1: Parse requirements and language",
                "Step 2: Prepare code generation prompt with:",
                "  - Clear specifications",
                "  - Language-specific best practices",
                "  - Style guidelines",
                "  - Example format",
                "Step 3: Use HybridPrompting algorithm",
                "Step 4: Send to LLM (use SmartRouter for tier)",
                "Step 5: Parse code from response",
                "Step 6: Extract dependencies",
                "Step 7: Generate explanation",
                "Step 8: Return code + metadata"
            ],
            
            tags=["code-generation", "llm", "coding"],
            dependencies=["LLMQuery", "HybridPrompting", "SmartModelRouter"]
        )
    
    def execute(self, params: Dict[str, Any]) -> AlgorithmResult:
        """Execute code generation"""
        
        requirements = params.get("requirements", "")
        language = params.get("language", "python")
        context = params.get("context", "")
        style = params.get("style", "clean")
        
        print(f"\n💻 Code Generator: '{requirements[:60]}...'")
        print(f"   Language: {language} | Style: {style}")
        
        try:
            # Step 2: Prepare specialized prompt
            prompt = self._create_code_prompt(requirements, language, context, style)
            
            # Step 3-4: Use LLM
            # TODO: Use actual LLMQuery + SmartRouter algorithms
            # For now, generate template code
            
            code = self._generate_template_code(requirements, language)
            explanation = f"Generated {language} code for: {requirements}"
            dependencies = self._extract_dependencies(code, language)
            
            print(f"   ✅ Generated {len(code)} chars of {language} code")
            
            return AlgorithmResult(
                status="success",
                data={
                    "code": code,
                    "explanation": explanation,
                    "dependencies": dependencies
                },
                metadata={
                    "language": language,
                    "style": style,
                    "lines_of_code": code.count('\n') + 1
                }
            )
        
        except Exception as e:
            return AlgorithmResult(status="error", error=f"Code generation failed: {str(e)}")
    
    def _create_code_prompt(self, requirements: str, language: str, context: str, style: str) -> str:
        """Create specialized code generation prompt"""
        
        prompt = f"""You are an expert {language} developer.

Task: {requirements}

Requirements:
- Language: {language}
- Style: {style} code (readable, maintainable, efficient)
- Include error handling
- Add docstrings/comments
- Follow best practices
"""
        
        if context:
            prompt += f"\nCodebase Context:\n{context}\n"
        
        prompt += f"\nGenerate complete, production-ready {language} code."
        
        return prompt
    
    def _generate_template_code(self, requirements: str, language: str) -> str:
        """Generate template code (placeholder until LLM integrated)"""
        
        templates = {
            "python": f'''"""
{requirements}
"""

def main():
    """Main function"""
    # TODO: Implement {requirements}
    pass

if __name__ == "__main__":
    main()
''',
            "javascript": f'''/**
 * {requirements}
 */

function main() {{
    // TODO: Implement {requirements}
}}

main();
''',
            "go": f'''package main

import "fmt"

// {requirements}
func main() {{
    // TODO: Implement {requirements}
}}
'''
        }
        
        return templates.get(language, templates["python"])
    
    def _extract_dependencies(self, code: str, language: str) -> list:
        """Extract dependencies from code"""
        
        deps = []
        
        if language == "python":
            # Look for import statements
            for line in code.split('\n'):
                if line.strip().startswith('import ') or line.strip().startswith('from '):
                    deps.append(line.strip())
        
        return deps


def register(algorithm_manager):
    """Register Code Generator Algorithm"""
    try:
        algo = CodeGeneratorAlgorithm()
        algorithm_manager.register("CodeGenerator", algo)
        print("✅ Code Generator Algorithm registered")
    except Exception as e:
        print(f"❌ Failed to register CodeGenerator: {e}")
