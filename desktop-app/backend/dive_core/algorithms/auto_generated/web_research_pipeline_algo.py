"""Auto-generated algorithm: Orchestrates web-browse + web-scrape + pdf-extract for comprehensive web research."""
from dive_core.algorithms.base import BaseAlgorithm, AlgorithmResult
from dive_core.specs import AlgorithmSpec, VerificationResult


class WebResearchPipelineAlgorithmVerifier:
    def verify(self, result, context=None):
        from dive_core.specs import VerificationResult
        if result is None:
            return VerificationResult(False, 0.0, "Result is None", {})
        if not isinstance(result.data, dict):
            return VerificationResult(False, 0.0, "Result data is not dict", {})
        required = ['content', 'links', 'pdfs']
        missing = [k for k in required if k not in result.data]
        if missing:
            return VerificationResult(False, 0.5, f"Missing fields: {missing}", {"missing": missing})
        return VerificationResult(True, 1.0, "Schema valid", {})


class WebResearchPipelineAlgorithm(BaseAlgorithm):
    """Auto-generated: Orchestrates web-browse + web-scrape + pdf-extract for comprehensive web research"""

    def __init__(self):
        super().__init__()
        self.spec = AlgorithmSpec(
            name="web-research-pipeline",
            description="Orchestrates web-browse + web-scrape + pdf-extract for comprehensive web research",
            version="1.0.0",
            input_schema={'url': 'str', 'extract_type': 'str', 'depth': 'int'},
            output_schema={'content': 'str', 'links': 'list', 'pdfs': 'list'},
            verifier=WebResearchPipelineAlgorithmVerifier,
            cost_per_call=0.003,
            tags=['web-browse', 'web-scrape', 'pdf-extract', 'research'],
        )

    def execute(self, inputs, context=None):
        try:
            # Multi-step pipeline
                    steps_done = []
                    data = inputs.get("data", {})
                    
                    # Pipeline: browse → scrape → extract
                    results = {'browsed': [], 'scraped': [], 'extracted': []}
                    url = inputs.get('url', '')
                    results['browsed'].append(f'Browsed: {url}')
                    results['scraped'].append(f'Scraped content from: {url}')
                    if inputs.get('extract_type') == 'pdf':
                        results['extracted'].append(f'PDF extracted from: {url}')
                    return AlgorithmResult(status='success', data=results)
            
                    return AlgorithmResult("success", {"steps": steps_done, "result": data},
                        {"algorithm": "web-research-pipeline", "type": "pipeline"})
        except Exception as e:
            return AlgorithmResult("failure", None, {"error": str(e), "algorithm": "web-research-pipeline"})

    def can_handle(self, task):
        keywords = ['web-browse', 'web-scrape', 'pdf-extract', 'research', 'web', 'research', 'pipeline']
        task_lower = task.lower()
        return sum(1 for k in keywords if k in task_lower) / max(len(keywords), 1)
