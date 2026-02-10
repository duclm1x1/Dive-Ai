"""Auto-generated algorithm: Count words in text."""
from dive_core.algorithms.base import BaseAlgorithm, AlgorithmResult
from dive_core.specs import AlgorithmSpec, VerificationResult



class WordCounterAlgorithm(BaseAlgorithm):
    """Auto-generated: Count words in text"""

    def __init__(self):
        super().__init__()
        self.spec = AlgorithmSpec(
            name="word_counter",
            description="Count words in text",
            version="1.0.0",
            input_schema={},
            output_schema={},
            verifier=None,
            cost_per_call=0.0,
            tags=['word_counter'],
        )

    def execute(self, inputs, context=None):
        try:
            # Transform input data
                    result = {}
                    for k, v in inputs.items():
                        result[k] = v
                    t = str(inputs.get('text', ''))
                    result['words'] = len(t.split())
                    result['chars'] = len(t)
                    result['lines'] = t.count(chr(10))+1
                    return AlgorithmResult("success", result, {"algorithm": "word_counter", "type": "transform"})
        except Exception as e:
            return AlgorithmResult("failure", None, {"error": str(e), "algorithm": "word_counter"})

    def can_handle(self, task):
        keywords = ['word_counter', 'word_counter']
        task_lower = task.lower()
        return sum(1 for k in keywords if k in task_lower) / max(len(keywords), 1)
