#!/usr/bin/env python3
"""
Smartest Base Model for Next-Word Prediction
Based on Andrej Karpathy's principle: "The smartest base model because there's no fine-tuning"

Techniques:
1. Advanced Prompt Engineering
2. In-Context Learning (Few-Shot)
3. Chain-of-Thought Reasoning
4. Retrieval-Augmented Generation
5. Intelligent Ensemble
6. No Fine-Tuning (Preserve Base Model Intelligence)
"""

import openai
import tiktoken
import numpy as np
from typing import Dict, List, Tuple, Optional
import logging
from collections import Counter, defaultdict
from dataclasses import dataclass
import json
from datetime import datetime
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set OpenAI API key
openai.api_key = os.environ.get("OPENAI_API_KEY")


# ========== DATA STRUCTURES ==========

@dataclass
class SmartPredictionResult:
    """Result from smartest base model prediction"""
    input_text: str
    predicted_word: str
    probability: float
    confidence: float
    top_5: List[Tuple[str, float]]
    reasoning: str
    prompt_strategy: str
    model_used: str
    tokens_used: int
    timestamp: str


# ========== PROMPT ENGINEERING ==========

class AdvancedPromptEngineer:
    """Advanced prompt engineering for base models"""
    
    def __init__(self):
        self.encoding = tiktoken.get_encoding("cl100k_base")
        logger.info("Initialized Advanced Prompt Engineer")
    
    def create_base_prompt(self, text: str, strategy: str = "direct") -> str:
        """Create optimized prompt for base model"""
        
        if strategy == "direct":
            return self._direct_prompt(text)
        elif strategy == "cot":
            return self._chain_of_thought_prompt(text)
        elif strategy == "few_shot":
            return self._few_shot_prompt(text)
        elif strategy == "contextual":
            return self._contextual_prompt(text)
        elif strategy == "linguistic":
            return self._linguistic_prompt(text)
        else:
            return self._direct_prompt(text)
    
    def _direct_prompt(self, text: str) -> str:
        """Direct prediction prompt"""
        return f"""Given the text: "{text}"

What is the most likely next word?
Provide the next word and explain your reasoning based on:
1. Grammar and syntax
2. Semantic context
3. Common language patterns

Next word:"""
    
    def _chain_of_thought_prompt(self, text: str) -> str:
        """Chain-of-thought reasoning prompt"""
        return f"""Analyze the text step by step: "{text}"

Step 1: Identify the grammatical structure and part of speech needed
Step 2: Consider the semantic meaning and context
Step 3: Think about common word sequences
Step 4: Evaluate probability of each candidate word
Step 5: Select the most likely next word

Let me think through this:
- Grammar analysis: 
- Semantic context:
- Common patterns:
- Most likely word:

Next word:"""
    
    def _few_shot_prompt(self, text: str) -> str:
        """Few-shot learning prompt"""
        examples = [
            ("The capital of France is", "Paris"),
            ("Machine learning is a type of", "artificial"),
            ("The sum of 2 + 3 is", "5"),
            ("I love to eat", "food"),
            ("The weather today is", "sunny")
        ]
        
        prompt = "Complete the following text patterns:\n\n"
        
        for example_text, example_answer in examples:
            prompt += f'"{example_text}" → "{example_answer}"\n'
        
        prompt += f'\nNow complete this:\n"{text}" → '
        
        return prompt
    
    def _contextual_prompt(self, text: str) -> str:
        """Contextual understanding prompt"""
        # Extract context clues
        words = text.split()
        recent_words = " ".join(words[-5:]) if len(words) > 5 else text
        
        return f"""Analyze the immediate context and predict the next word.

Full context: "{text}"
Recent context (last 5 words): "{recent_words}"

Consider:
1. What word class is needed? (noun, verb, adjective, etc.)
2. What semantic field are we in?
3. What are the collocations?
4. What is the most natural continuation?

Most likely next word:"""
    
    def _linguistic_prompt(self, text: str) -> str:
        """Linguistic analysis prompt"""
        return f"""Perform linguistic analysis for: "{text}"

Linguistic features:
- Part of speech pattern: [analyze]
- Semantic field: [identify]
- Collocation patterns: [list]
- Frequency analysis: [consider]
- Register/style: [determine]

Based on linguistic analysis, the next word is:"""
    
    def estimate_token_usage(self, prompt: str) -> int:
        """Estimate tokens used in prompt"""
        return len(self.encoding.encode(prompt))


# ========== IN-CONTEXT LEARNING ==========

class InContextLearner:
    """In-context learning with few-shot examples"""
    
    def __init__(self):
        self.examples_db = self._build_examples_db()
        logger.info("Initialized In-Context Learner")
    
    def _build_examples_db(self) -> Dict[str, List[Tuple[str, str]]]:
        """Build database of examples"""
        return {
            'grammar': [
                ("The quick brown", "fox"),
                ("She is very", "smart"),
                ("He went to the", "store"),
                ("I like to eat", "pizza"),
                ("The weather is", "sunny")
            ],
            'numbers': [
                ("2 + 3 =", "5"),
                ("10 * 5 =", "50"),
                ("100 / 2 =", "50"),
                ("The year is 20", "24"),
                ("Pi is approximately", "3.14")
            ],
            'knowledge': [
                ("The capital of France is", "Paris"),
                ("The largest planet is", "Jupiter"),
                ("The speed of light is", "299,792,458"),
                ("The author of Harry Potter is", "Rowling"),
                ("The first president was", "Washington")
            ],
            'semantic': [
                ("Happy is to sad as big is to", "small"),
                ("Doctor is to hospital as teacher is to", "school"),
                ("Red is a color, blue is a", "color"),
                ("Monday is a day, January is a", "month"),
                ("Cat is an animal, rose is a", "flower")
            ]
        }
    
    def select_relevant_examples(self, text: str, num_examples: int = 3) -> List[Tuple[str, str]]:
        """Select most relevant examples for in-context learning"""
        
        # Determine category
        if any(word in text.lower() for word in ['capital', 'president', 'author', 'planet']):
            category = 'knowledge'
        elif any(word in text.lower() for word in ['+', '-', '*', '/', '=', 'sum', 'multiply']):
            category = 'numbers'
        elif any(word in text.lower() for word in ['is to', 'like', 'as', 'similar']):
            category = 'semantic'
        else:
            category = 'grammar'
        
        examples = self.examples_db.get(category, self.examples_db['grammar'])
        
        return examples[:num_examples]
    
    def create_few_shot_prompt(self, text: str, num_examples: int = 3) -> str:
        """Create few-shot prompt with relevant examples"""
        examples = self.select_relevant_examples(text, num_examples)
        
        prompt = "Complete the text patterns:\n\n"
        
        for example_text, example_answer in examples:
            prompt += f'Input: "{example_text}"\nOutput: "{example_answer}"\n\n'
        
        prompt += f'Input: "{text}"\nOutput: '
        
        return prompt


# ========== CHAIN-OF-THOUGHT REASONING ==========

class ChainOfThoughtReasoner:
    """Chain-of-thought reasoning for better predictions"""
    
    def __init__(self):
        logger.info("Initialized Chain-of-Thought Reasoner")
    
    def create_reasoning_prompt(self, text: str) -> str:
        """Create prompt that encourages step-by-step reasoning"""
        
        return f"""Let me think step by step about what word comes next.

Text: "{text}"

Step 1 - Grammar Analysis:
What part of speech is needed? What grammatical role should the next word play?

Step 2 - Semantic Analysis:
What is the semantic meaning? What topic are we discussing?

Step 3 - Context Analysis:
What are the recent words? What patterns do I see?

Step 4 - Frequency Analysis:
What are common word sequences? What do I know about language statistics?

Step 5 - Candidate Generation:
What are the top candidate words?

Step 6 - Probability Ranking:
Rank by likelihood:
1. 
2. 
3. 
4. 
5. 

Most likely next word:"""
    
    def extract_reasoning(self, response: str) -> Tuple[str, str]:
        """Extract prediction and reasoning from response"""
        
        # Try to find the answer
        lines = response.split('\n')
        
        for i, line in enumerate(lines):
            if 'most likely' in line.lower() or 'answer' in line.lower():
                # Get the word after the colon
                if ':' in line:
                    word = line.split(':')[-1].strip().strip('"').strip("'")
                    reasoning = '\n'.join(lines[:i])
                    return word, reasoning
        
        # Fallback: get last word mentioned
        words = response.split()
        if words:
            return words[-1].strip('"').strip("'"), response
        
        return "", response


# ========== RETRIEVAL-AUGMENTED GENERATION ==========

class RetrievalAugmentedGenerator:
    """Retrieval-augmented generation for context"""
    
    def __init__(self):
        self.knowledge_base = self._build_knowledge_base()
        logger.info("Initialized Retrieval-Augmented Generator")
    
    def _build_knowledge_base(self) -> Dict[str, List[str]]:
        """Build knowledge base of common patterns"""
        return {
            'phrases': [
                "The quick brown fox jumps over the lazy dog",
                "Machine learning is a subset of artificial intelligence",
                "The capital of France is Paris",
                "I love to spend time with my family",
                "The weather today is sunny and warm",
                "She is one of the most talented musicians",
                "He decided to pursue a career in engineering",
                "The project was completed ahead of schedule",
                "We need to improve our communication skills",
                "The results exceeded our expectations"
            ],
            'collocations': {
                'very': ['good', 'bad', 'nice', 'smart', 'tired', 'happy', 'sad'],
                'the': ['cat', 'dog', 'house', 'car', 'book', 'person', 'time'],
                'to': ['go', 'eat', 'sleep', 'work', 'play', 'read', 'write'],
                'is': ['good', 'bad', 'nice', 'smart', 'tired', 'happy', 'sad']
            }
        }
    
    def retrieve_context(self, text: str) -> str:
        """Retrieve relevant context from knowledge base"""
        
        # Find similar phrases
        text_lower = text.lower()
        similar_phrases = []
        
        for phrase in self.knowledge_base['phrases']:
            if any(word in phrase.lower() for word in text_lower.split()):
                similar_phrases.append(phrase)
        
        context = "Similar patterns in knowledge base:\n"
        for phrase in similar_phrases[:3]:
            context += f"- {phrase}\n"
        
        return context
    
    def create_rag_prompt(self, text: str) -> str:
        """Create RAG-enhanced prompt"""
        
        context = self.retrieve_context(text)
        
        return f"""Use the following context to predict the next word.

Context:
{context}

Text: "{text}"

Based on the context and patterns, the next word is:"""


# ========== SMARTEST BASE MODEL ==========

class SmartestBaseModel:
    """The Smartest Base Model - No Fine-Tuning"""
    
    def __init__(self, model: str = "gpt-3.5-turbo"):
        self.model = model
        self.prompt_engineer = AdvancedPromptEngineer()
        self.in_context_learner = InContextLearner()
        self.cot_reasoner = ChainOfThoughtReasoner()
        self.rag_generator = RetrievalAugmentedGenerator()
        
        logger.info(f"Initialized Smartest Base Model using {model}")
    
    def predict_smart(self, text: str, strategy: str = "ensemble") -> SmartPredictionResult:
        """
        Predict next word using smartest base model
        
        Strategy options:
        - 'direct': Simple prompt
        - 'cot': Chain-of-thought
        - 'few_shot': Few-shot learning
        - 'contextual': Contextual analysis
        - 'linguistic': Linguistic analysis
        - 'rag': Retrieval-augmented
        - 'ensemble': Combine all strategies
        """
        
        if strategy == "ensemble":
            return self._ensemble_predict(text)
        else:
            return self._single_strategy_predict(text, strategy)
    
    def _single_strategy_predict(self, text: str, strategy: str) -> SmartPredictionResult:
        """Predict using single strategy"""
        
        # Create prompt
        if strategy == "cot":
            prompt = self.cot_reasoner.create_reasoning_prompt(text)
        elif strategy == "few_shot":
            prompt = self.in_context_learner.create_few_shot_prompt(text)
        elif strategy == "rag":
            prompt = self.rag_generator.create_rag_prompt(text)
        else:
            prompt = self.prompt_engineer.create_base_prompt(text, strategy)
        
        # Get response from base model
        response = self._call_base_model(prompt)
        
        # Extract prediction
        predicted_word = self._extract_prediction(response)
        
        # Parse top-5
        top_5 = self._parse_top_5(response)
        
        # Calculate confidence
        confidence = self._calculate_confidence(response, predicted_word)
        
        tokens_used = self.prompt_engineer.estimate_token_usage(prompt)
        
        return SmartPredictionResult(
            input_text=text,
            predicted_word=predicted_word,
            probability=confidence,
            confidence=confidence,
            top_5=top_5,
            reasoning=response[:200],
            prompt_strategy=strategy,
            model_used=self.model,
            tokens_used=tokens_used,
            timestamp=datetime.now().isoformat()
        )
    
    def _ensemble_predict(self, text: str) -> SmartPredictionResult:
        """Ensemble prediction using all strategies"""
        
        strategies = ["direct", "cot", "few_shot", "contextual", "rag"]
        predictions = defaultdict(float)
        all_responses = []
        
        for strategy in strategies:
            result = self._single_strategy_predict(text, strategy)
            all_responses.append(result.reasoning)
            
            # Add predictions with equal weight
            for word, prob in result.top_5:
                predictions[word] += prob / len(strategies)
        
        # Get top prediction
        sorted_preds = sorted(predictions.items(), key=lambda x: x[1], reverse=True)
        top_5 = sorted_preds[:5]
        
        predicted_word = top_5[0][0] if top_5 else ""
        confidence = top_5[0][1] if top_5 else 0
        
        combined_reasoning = "\n".join(all_responses[:100])
        
        return SmartPredictionResult(
            input_text=text,
            predicted_word=predicted_word,
            probability=confidence,
            confidence=confidence,
            top_5=top_5,
            reasoning=combined_reasoning,
            prompt_strategy="ensemble",
            model_used=self.model,
            tokens_used=0,
            timestamp=datetime.now().isoformat()
        )
    
    def _call_base_model(self, prompt: str) -> str:
        """Call base model API without fine-tuning"""
        
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at predicting the next word in text sequences. Provide clear, concise predictions."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=200,
                top_p=0.9
            )
            
            return response['choices'][0]['message']['content']
        
        except Exception as e:
            logger.error(f"Error calling base model: {e}")
            return ""
    
    def _extract_prediction(self, response: str) -> str:
        """Extract predicted word from response"""
        
        # Look for quoted words
        quoted = re.findall(r'"([^"]+)"', response)
        if quoted:
            return quoted[-1]
        
        # Look for words after common patterns
        patterns = [
            r'next word[:\s]+(\w+)',
            r'word[:\s]+(\w+)',
            r'answer[:\s]+(\w+)',
            r'prediction[:\s]+(\w+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, response, re.IGNORECASE)
            if match:
                return match.group(1)
        
        # Get last word
        words = response.split()
        return words[-1] if words else ""
    
    def _parse_top_5(self, response: str) -> List[Tuple[str, float]]:
        """Parse top-5 predictions from response"""
        
        # Try to find numbered list
        lines = response.split('\n')
        top_5 = []
        
        for line in lines:
            # Match patterns like "1. word - 0.95" or "1) word (95%)"
            match = re.search(r'[\d.]+[\s.)\-]+(["\']?)(\w+)\1', line)
            if match:
                word = match.group(2)
                
                # Try to extract probability
                prob_match = re.search(r'(\d+\.?\d*)\s*%?', line)
                prob = float(prob_match.group(1)) / 100 if prob_match else 0.5
                
                top_5.append((word, prob))
        
        # If no structured list, return empty
        return top_5[:5] if top_5 else []
    
    def _calculate_confidence(self, response: str, predicted_word: str) -> float:
        """Calculate confidence score"""
        
        # Check for confidence indicators
        confidence_words = {
            'definitely': 0.95,
            'certainly': 0.90,
            'likely': 0.75,
            'probably': 0.70,
            'possibly': 0.60,
            'maybe': 0.50
        }
        
        response_lower = response.lower()
        
        for word, score in confidence_words.items():
            if word in response_lower:
                return score
        
        # Default confidence
        return 0.7


# ========== MAIN ==========

def main():
    """Example usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Smartest Base Model - No Fine-Tuning")
    parser.add_argument("--text", default="The quick brown fox jumps over the", help="Input text")
    parser.add_argument("--strategy", choices=["direct", "cot", "few_shot", "contextual", "linguistic", "rag", "ensemble"], default="ensemble", help="Strategy")
    parser.add_argument("--model", default="gpt-3.5-turbo", help="Base model to use")
    
    args = parser.parse_args()
    
    # Initialize smartest base model
    model = SmartestBaseModel(model=args.model)
    
    # Make prediction
    logger.info(f"Input: '{args.text}'")
    logger.info(f"Strategy: {args.strategy}")
    
    result = model.predict_smart(args.text, strategy=args.strategy)
    
    print("\n" + "="*80)
    print("SMARTEST BASE MODEL PREDICTION")
    print("="*80)
    print(f"Input: '{result.input_text}'")
    print(f"Predicted word: '{result.predicted_word}'")
    print(f"Probability: {result.probability:.4f}")
    print(f"Confidence: {result.confidence:.1%}")
    print(f"Strategy: {result.prompt_strategy}")
    print(f"Model: {result.model_used}")
    print(f"Tokens used: {result.tokens_used}")
    print(f"\nTop 5 predictions:")
    for i, (word, prob) in enumerate(result.top_5, 1):
        print(f"  {i}. '{word}' - {prob:.4f}")
    print(f"\nReasoning:\n{result.reasoning[:300]}")
    print("="*80)


if __name__ == "__main__":
    import os
    main()
