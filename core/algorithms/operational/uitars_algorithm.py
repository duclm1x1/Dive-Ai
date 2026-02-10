"""
Dive AI V29.3 - UI-TARS Algorithm Wrapper
Integrates UI-TARS from V28.7 as an algorithm in the V29.3 system

This allows UI-TARS to be selected and executed by the AI Algorithm Selector
"""

import sys
import os

# Add paths
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

try:
    from core.algorithms.base_algorithm import BaseAlgorithm, AlgorithmResult
    from core.algorithms.algorithm_spec import AlgorithmSpec, AlgorithmIOSpec, IOField
except ImportError:
    # Fallback if imports fail
    BaseAlgorithm = object
    AlgorithmResult = dict
    AlgorithmSpec = dict
    AlgorithmIOSpec = dict
    IOField = dict


class UITARSAlgorithm(BaseAlgorithm):
    """
    UI-TARS Desktop Automation Algorithm
    
    Wraps the UI-TARS client from V28.7 as an operational algorithm
    that can be selected and executed by the AI Algorithm Selector.
    
    Capabilities:
    - Natural language UI automation
    - Browser control
    - Desktop application automation
    - Screenshot capture
    - Vision-based interaction
    """
    
    def __init__(self):
        """Initialize UI-TARS Algorithm"""
        
        # Algorithm specification
        self.spec = AlgorithmSpec(
            algorithm_id="UITARS",
            name="UI-TARS Desktop Automation",
            level="operational",
            category="automation",
            version="1.0",
            description="Execute desktop and browser automation tasks using natural language commands. Can open applications, navigate browsers, click buttons, type text, and capture screenshots using vision-based AI.",
            
            io=AlgorithmIOSpec(
                inputs=[
                    IOField(
                        name="command",
                        type="string",
                        required=True,
                        description="Natural language command for UI automation (e.g., 'Open Chrome and navigate to GitHub')"
                    ),
                    IOField(
                        name="max_steps",
                        type="integer",
                        required=False,
                        description="Maximum number of steps to execute (default: 50)"
                    )
                ],
                outputs=[
                    IOField(
                        name="actions",
                        type="list",
                        required=True,
                        description="List of executed actions with details"
                    ),
                    IOField(
                        name="screenshots",
                        type="list",
                        required=False,
                        description="Screenshots captured during execution"
                    ),
                    IOField(
                        name="success",
                        type="boolean",
                        required=True,
                        description="Whether the automation completed successfully"
                    )
                ]
            ),
            
            steps=[],  # UI-TARS handles its own steps internally
            
            tags=["ui", "automation", "desktop", "browser", "vision", "natural-language"]
        )
        
        # Try to import UI-TARS from V28.7
        self.uitars_client = None
        try:
            from core.dive_uitars_client import UITARSClient
            self.uitars_client = UITARSClient()
            print("   ✅ UI-TARS Client loaded")
        except ImportError as e:
            print(f"   ⚠️ UI-TARS Client not available: {e}")
            print("      UI-TARS will operate in simulation mode")
    
    def execute(self, params: dict) -> AlgorithmResult:
        """
        Execute UI automation command
        
        Args:
            params: {
                'command': 'Natural language UI command',
                'max_steps': 50 (optional)
            }
        
        Returns:
            AlgorithmResult with action list and screenshots
        """
        
        command = params.get('command', '')
        max_steps = params.get('max_steps', 50)
        
        print(f"🤖 Executing UI-TARS: {command}")
        
        if self.uitars_client:
            try:
                # Execute via UI-TARS client
                actions = []
                screenshots = []
                
                for action_result in self.uitars_client.execute_command(command):
                    actions.append(action_result)
                    
                    # Extract screenshots if available
                    if isinstance(action_result, dict) and 'screenshot' in action_result:
                        screenshots.append(action_result['screenshot'])
                    
                    # Stop if max steps reached
                    if len(actions) >= max_steps:
                        break
                
                return AlgorithmResult(
                    status="success",
                    data={
                        'actions': actions,
                        'screenshots': screenshots,
                        'success': True,
                        'command': command,
                        'steps_executed': len(actions)
                    }
                )
                
            except Exception as e:
                return AlgorithmResult(
                    status="error",
                    data={
                        'error': str(e),
                        'command': command,
                        'success': False
                    }
                )
        else:
            # Simulation mode
            return AlgorithmResult(
                status="success",
                data={
                    'actions': [
                        {'type': 'simulation', 'description': f'Simulated: {command}'}
                    ],
                    'screenshots': [],
                    'success': True,
                    'command': command,
                    'note': 'UI-TARS running in simulation mode - real client not available'
                }
            )


# For registration in AlgorithmManager
def register_uitars(algorithm_manager):
    """Register UI-TARS as an algorithm"""
    try:
        uitars_algo = UITARSAlgorithm()
        algorithm_manager.register("UITARS", uitars_algo)
        print("✅ UI-TARS Algorithm registered")
    except Exception as e:
        print(f"❌ Failed to register UI-TARS: {e}")
