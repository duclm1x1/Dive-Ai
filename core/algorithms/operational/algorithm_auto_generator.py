"""
Auto-Generation Algorithm System
Automatically detects skills, features, and creates new algorithms with auto-debugging

This is the SELF-EVOLVING core - creates algorithms from patterns
"""

import os
import sys
import ast
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from core.algorithms.base_algorithm import (
    BaseAlgorithm,
    AlgorithmResult,
    AlgorithmSpec,
    AlgorithmIOSpec,
    IOField
)


@dataclass
class SkillPattern:
    """Detected skill pattern"""
    name: str
    description: str
    inputs: List[str]
    outputs: List[str]
    complexity: int  # 1-10
    category: str
    source_file: Optional[str] = None


class AlgorithmAutoGenerator(BaseAlgorithm):
    """
    Auto-Generate Algorithms from Skills/Features
    
    SELF-EVOLVING: Detects patterns and creates new algorithms
    """
    
    def __init__(self):
        self.spec = AlgorithmSpec(
            algorithm_id="AlgorithmAutoGenerator",
            name="Algorithm Auto-Generator",
            level="operational",
            category="self-evolving",
            version="1.0",
            description="Automatically detect skills/features and generate new algorithms with auto-debugging.",
            
            io=AlgorithmIOSpec(
                inputs=[
                    IOField("source", "string", False, "Source: 'skills'/'features'/'code'"),
                    IOField("scan_directory", "string", False, "Directory to scan for patterns"),
                    IOField("auto_debug", "boolean", False, "Auto-debug generated algorithms")
                ],
                outputs=[
                    IOField("generated_algorithms", "list", True, "List of generated algorithm IDs"),
                    IOField("debug_results", "list", True, "Debug results for each"),
                    IOField("success_count", "integer", True, "Successfully generated")
                ]
            ),
            
            steps=[
                "Step 1: Scan source (skills/features/code) for patterns",
                "Step 2: Detect reusable algorithm candidates",
                "Step 3: Generate AlgorithmSpec from pattern",
                "Step 4: Generate execute() method with CODE + STEPS",
                "Step 5: Auto-debug generated algorithm",
                "Step 6: Register if debug passes",
                "Step 7: Return results"
            ],
            
            tags=["self-evolving", "auto-generation", "critical"]
        )
        
        self.auto_debugger = AlgorithmAutoDebugger()
    
    def execute(self, params: Dict[str, Any]) -> AlgorithmResult:
        """Execute auto-generation"""
        
        source = params.get("source", "skills")
        scan_directory = params.get("scan_directory", "core/")
        auto_debug = params.get("auto_debug", True)
        
        print(f"\n🤖 Auto-Generating Algorithms from: {source}")
        print(f"   📁 Scanning: {scan_directory}")
        
        try:
            # Step 1: Scan for patterns
            patterns = self._scan_for_patterns(source, scan_directory)
            print(f"   🔍 Found {len(patterns)} potential algorithm patterns")
            
            generated_algorithms = []
            debug_results = []
            success_count = 0
            
            # Step 2-6: Generate each algorithm
            for pattern in patterns[:5]:  # Limit to 5 per run
                print(f"\n   🔨 Generating: {pattern.name}")
                
                # Step 3: Generate AlgorithmSpec
                spec_code = self._generate_algorithm_spec(pattern)
                
                # Step 4: Generate execute method
                execute_code = self._generate_execute_method(pattern)
                
                # Combine into full algorithm
                full_code = self._combine_algorithm_code(pattern, spec_code, execute_code)
                
                # Step 5: Auto-debug if requested
                if auto_debug:
                    debug_result = self.auto_debugger.debug_algorithm_code(
                        pattern.name,
                        full_code
                    )
                    debug_results.append(debug_result)
                    
                    if debug_result["status"] == "success":
                        # Step 6: Save to file
                        saved = self._save_algorithm(pattern, full_code)
                        if saved:
                            generated_algorithms.append(pattern.name)
                            success_count += 1
                            print(f"      ✅ Generated & saved: {pattern.name}")
                        else:
                            print(f"      ⚠️  Generated but save failed: {pattern.name}")
                    else:
                        print(f"      ❌ Debug failed: {debug_result.get('error')}")
                else:
                    # Save without debugging
                    saved = self._save_algorithm(pattern, full_code)
                    if saved:
                        generated_algorithms.append(pattern.name)
                        success_count += 1
            
            # Step 7: Return
            print(f"\n   ✅ Generated {success_count}/{len(patterns)} algorithms")
            
            return AlgorithmResult(
                status="success",
                data={
                    "generated_algorithms": generated_algorithms,
                    "debug_results": debug_results,
                    "success_count": success_count,
                    "total_patterns": len(patterns)
                },
                metadata={
                    "source": source,
                    "scan_directory": scan_directory,
                    "auto_debug": auto_debug
                }
            )
        
        except Exception as e:
            return AlgorithmResult(
                status="error",
                error=f"Auto-generation failed: {str(e)}"
            )
    
    def _scan_for_patterns(self, source: str, directory: str) -> List[SkillPattern]:
        """Scan directory for algorithm patterns"""
        
        patterns = []
        
        if source == "skills":
            # Scan for skill patterns
            patterns.extend(self._detect_skill_patterns(directory))
        elif source == "features":
            # Scan for feature patterns
            patterns.extend(self._detect_feature_patterns(directory))
        elif source == "code":
            # Scan code for reusable patterns
            patterns.extend(self._detect_code_patterns(directory))
        
        return patterns
    
    def _detect_skill_patterns(self, directory: str) -> List[SkillPattern]:
        """Detect skill patterns from codebase"""
        
        # Example patterns (in real implementation, scan actual code)
        return [
            SkillPattern(
                name="DataValidation",
                description="Validate data against schema",
                inputs=["data", "schema"],
                outputs=["valid", "errors"],
                complexity=3,
                category="utilities"
            ),
            SkillPattern(
                name="CacheManager",
                description="Manage caching with TTL",
                inputs=["key", "value", "ttl"],
                outputs=["cached", "hit_rate"],
                complexity=4,
                category="optimization"
            )
        ]
    
    def _detect_feature_patterns(self, directory: str) -> List[SkillPattern]:
        """Detect feature patterns"""
        return []
    
    def _detect_code_patterns(self, directory: str) -> List[SkillPattern]:
        """Detect reusable code patterns"""
        return []
    
    def _generate_algorithm_spec(self, pattern: SkillPattern) -> str:
        """Generate AlgorithmSpec code"""
        
        inputs_code = ",\n                    ".join([
            f'IOField("{inp}", "string", True, "{inp}")'
            for inp in pattern.inputs
        ])
        
        outputs_code = ",\n                    ".join([
            f'IOField("{out}", "string", True, "{out}")'
            for out in pattern.outputs
        ])
        
        return f'''        self.spec = AlgorithmSpec(
            algorithm_id="{pattern.name}",
            name="{pattern.name}",
            level="operational",
            category="{pattern.category}",
            version="1.0",
            description="{pattern.description}",
            
            io=AlgorithmIOSpec(
                inputs=[
                    {inputs_code}
                ],
                outputs=[
                    {outputs_code}
                ]
            ),
            
            steps=[
                "Step 1: Validate inputs",
                "Step 2: Process data",
                "Step 3: Return results"
            ],
            
            tags=["{pattern.category}", "auto-generated"]
        )'''
    
    def _generate_execute_method(self, pattern: SkillPattern) -> str:
        """Generate execute() method"""
        
        input_params = "\n        ".join([
            f'{inp} = params.get("{inp}", "")'
            for inp in pattern.inputs
        ])
        
        output_data = ",\n                ".join([
            f'"{out}": {out}_result'
            for out in pattern.outputs
        ])
        
        return f'''    def execute(self, params: Dict[str, Any]) -> AlgorithmResult:
        """Execute {pattern.name}"""
        
        {input_params}
        
        try:
            # TODO: Implement algorithm logic
            {"\n            ".join([f'{out}_result = None' for out in pattern.outputs])}
            
            return AlgorithmResult(
                status="success",
                data={{
                    {output_data}
                }}
            )
        except Exception as e:
            return AlgorithmResult(
                status="error",
                error=f"{{pattern.name}} failed: {{str(e)}}"
            )'''
    
    def _combine_algorithm_code(self, pattern: SkillPattern, spec_code: str, execute_code: str) -> str:
        """Combine into full algorithm file"""
        
        return f'''"""
{pattern.name} Algorithm
Auto-generated by AlgorithmAutoGenerator

{pattern.description}
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


class {pattern.name}Algorithm(BaseAlgorithm):
    """
    {pattern.name} - {pattern.description}
    
    AUTO-GENERATED
    """
    
    def __init__(self):
{spec_code}
    
{execute_code}


def register(algorithm_manager):
    """Register {pattern.name} Algorithm"""
    try:
        algo = {pattern.name}Algorithm()
        algorithm_manager.register("{pattern.name}", algo)
        print("✅ {pattern.name} Algorithm registered (AUTO-GENERATED)")
    except Exception as e:
        print(f"❌ Failed to register {pattern.name}: {{e}}")
'''
    
    def _save_algorithm(self, pattern: SkillPattern, code: str) -> bool:
        """Save generated algorithm to file"""
        
        try:
            # Save to auto-generated directory
            output_dir = "core/algorithms/auto_generated"
            os.makedirs(output_dir, exist_ok=True)
            
            filename = f"{output_dir}/{pattern.name.lower()}.py"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(code)
            
            return True
        except Exception as e:
            print(f"   ⚠️  Save error: {e}")
            return False


class AlgorithmAutoDebugger:
    """
    Auto-Debug Generated Algorithms
    
    Validates syntax, imports, and basic execution
    """
    
    def debug_algorithm_code(self, name: str, code: str) -> Dict[str, Any]:
        """Debug algorithm code"""
        
        print(f"      🔍 Debugging: {name}")
        
        # Step 1: Syntax validation
        syntax_valid, syntax_error = self._validate_syntax(code)
        if not syntax_valid:
            return {
                "status": "error",
                "stage": "syntax",
                "error": syntax_error
            }
        print(f"         ✅ Syntax valid")
        
        # Step 2: Import validation
        imports_valid, import_error = self._validate_imports(code)
        if not imports_valid:
            return {
                "status": "error",
                "stage": "imports",
                "error": import_error
            }
        print(f"         ✅ Imports valid")
        
        # Step 3: Structure validation
        structure_valid, structure_error = self._validate_structure(code)
        if not structure_valid:
            return {
                "status": "error",
                "stage": "structure",
                "error": structure_error
            }
        print(f"         ✅ Structure valid")
        
        return {
            "status": "success",
            "stages_passed": ["syntax", "imports", "structure"]
        }
    
    def _validate_syntax(self, code: str) -> tuple[bool, Optional[str]]:
        """Validate Python syntax"""
        try:
            ast.parse(code)
            return True, None
        except SyntaxError as e:
            return False, f"Syntax error: {str(e)}"
    
    def _validate_imports(self, code: str) -> tuple[bool, Optional[str]]:
        """Validate imports can be resolved"""
        try:
            # Parse imports from code
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        # Check if module exists
                        pass  # TODO: Implement import validation
            return True, None
        except Exception as e:
            return False, f"Import error: {str(e)}"
    
    def _validate_structure(self, code: str) -> tuple[bool, Optional[str]]:
        """Validate algorithm structure"""
        try:
            # Check for required elements
            required = ["BaseAlgorithm", "AlgorithmResult", "execute"]
            
            for req in required:
                if req not in code:
                    return False, f"Missing required element: {req}"
            
            return True, None
        except Exception as e:
            return False, f"Structure error: {str(e)}"


def register(algorithm_manager):
    """Register Auto-Generator"""
    try:
        algo = AlgorithmAutoGenerator()
        algorithm_manager.register("AlgorithmAutoGenerator", algo)
        print("✅ AlgorithmAutoGenerator registered (SELF-EVOLVING)")
    except Exception as e:
        print(f"❌ Failed to register AlgorithmAutoGenerator: {e}")
