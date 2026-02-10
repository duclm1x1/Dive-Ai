"""
Vision Analysis Algorithm
Analyze screenshots with Claude 4.6 Opus vision capabilities

Algorithm = CODE + STEPS
⭐ CRITICAL for understanding what's on screen
"""

import os
import sys
import requests
from typing import Dict, Any

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from core.algorithms.base_algorithm import (
    BaseAlgorithm,
    AlgorithmResult,
    AlgorithmSpec,
    AlgorithmIOSpec,
    IOField
)


class VisionAnalysisAlgorithm(BaseAlgorithm):
    """
    Vision Analysis - AI-Powered Screen Understanding
    
    ⭐ CRITICAL: Uses Claude 4.6 Opus vision to understand what's on screen
    """
    
    def __init__(self):
        self.spec = AlgorithmSpec(
            algorithm_id="VisionAnalysis",
            name="Vision Analysis",
            level="operational",
            category="computer-control",
            version="1.0",
            description="Analyze screenshots using Claude 4.6 Opus vision. Understand UI elements, extract text, identify clickable areas.",
            
            io=AlgorithmIOSpec(
                inputs=[
                    IOField("screenshot_b64", "string", True, "Base64 encoded screenshot"),
                    IOField("prompt", "string", True, "What to analyze (e.g., 'Find login button')"),
                    IOField("provider", "string", False, "API provider (default: v98)")
                ],
                outputs=[
                    IOField("analysis", "string", True, "AI's understanding of the screen"),
                    IOField("elements_found", "list", False, "UI elements detected"),
                    IOField("coordinates", "object", False, "Element positions if found")
                ]
            ),
            
            steps=[
                "Step 1: Decode base64 screenshot (validate format)",
                "Step 2: Prepare vision request for Claude 4.6",
                "Step 3: Send image + prompt to LLM",
                "Step 4: Parse AI response",
                "Step 5: Extract element locations if mentioned",
                "Step 6: Return analysis + structured data"
            ],
            
            tags=["vision", "computer-control", "ai-powered", "CRITICAL"]
        )
    
    def execute(self, params: Dict[str, Any]) -> AlgorithmResult:
        """Execute vision analysis"""
        
        screenshot_b64 = params.get("screenshot_b64", "")
        prompt = params.get("prompt", "Describe what you see")
        provider = params.get("provider", "v98")
        
        print(f"\n👁️  Vision Analysis: '{prompt[:50]}...'")
        
        try:
            # Step 1: Validate screenshot
            if not screenshot_b64:
                return AlgorithmResult(status="error", error="No screenshot provided")
            
            # Step 2: Prepare vision request
            api_key = os.getenv("V98_API_KEY") if provider == "v98" else os.getenv("AICODING_API_KEY")
            api_url = "https://api.v98store.com/v1" if provider == "v98" else "https://api.aicoding.com/v1"
            
            if not api_key:
                return AlgorithmResult(status="error", error=f"No API key for {provider}")
            
            # Step 3: Send to LLM with vision
            payload = {
                "model": "claude-opus-4-6-thinking",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/png",
                                    "data": screenshot_b64
                                }
                            },
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ]
                    }
                ],
                "max_tokens": 2048
            }
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01"
            }
            
            response = requests.post(
                f"{api_url}/messages",
                headers=headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code != 200:
                return AlgorithmResult(
                    status="error",
                    error=f"Vision API error: HTTP {response.status_code}"
                )
            
            # Step 4: Parse response
            data = response.json()
            analysis = data.get("content", [{}])[0].get("text", "")
            
            print(f"   ✅ Analysis complete ({len(analysis)} chars)")
            
            # Step 5: Extract elements (simple parsing)
            elements_found = self._extract_elements(analysis)
            coordinates = self._extract_coordinates(analysis)
            
            # Step 6: Return
            return AlgorithmResult(
                status="success",
                data={
                    "analysis": analysis,
                    "elements_found": elements_found,
                    "coordinates": coordinates
                },
                metadata={
                    "prompt": prompt,
                    "provider": provider,
                    "model": "claude-opus-4-6-thinking"
                }
            )
        
        except requests.exceptions.RequestException as e:
            return AlgorithmResult(status="error", error=f"API request failed: {str(e)}")
        except KeyError as e:
            return AlgorithmResult(status="error", error=f"Invalid API response format: {str(e)}")
        except Exception as e:
            return AlgorithmResult(status="error", error=f"Vision analysis failed: {str(e)}")
    
    def _extract_elements(self, analysis: str) -> list:
        """Extract UI elements mentioned in analysis"""
        
        common_elements = ["button", "input", "text", "image", "link", "menu", "icon"]
        found = []
        
        analysis_lower = analysis.lower()
        for element in common_elements:
            if element in analysis_lower:
                found.append(element)
        
        return found
    
    def _extract_coordinates(self, analysis: str) -> dict:
        """Try to extract coordinates if mentioned"""
        
        # TODO: Implement coordinate extraction from natural language
        # For now, return empty
        return {}


def register(algorithm_manager):
    """Register Vision Analysis Algorithm"""
    try:
        algo = VisionAnalysisAlgorithm()
        algorithm_manager.register("VisionAnalysis", algo)
        print("✅ Vision Analysis Algorithm registered")
    except Exception as e:
        print(f"❌ Failed to register VisionAnalysis: {e}")
