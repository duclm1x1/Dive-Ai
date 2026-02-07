#!/usr/bin/env python3
"""
Advanced Numerical Token Predictor
Uses tiktoken for tokenization and predicts most probable next token
with deep numerical understanding and statistical analysis
"""

import tiktoken
import numpy as np
from typing import Dict, List, Tuple, Optional
import logging
from collections import Counter, defaultdict
import re
from dataclasses import dataclass
import json
from datetime import datetime
import math

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ========== DATA STRUCTURES ==========

@dataclass
class TokenInfo:
    """Information about a token"""
    token_id: int
    token_str: str
    is_numerical: bool
    numerical_value: Optional[float] = None
    is_operator: bool = False
    is_punctuation: bool = False


@dataclass
class PredictionResult:
    """Result of token prediction"""
    input_text: str
    input_tokens: List[int]
    predicted_token: str
    predicted_token_id: int
    probability: float
    confidence: float
    top_5_predictions: List[Tuple[str, float]]
    reasoning: str


# ========== TIKTOKEN INTEGRATION ==========

class TiktokenNumericalAnalyzer:
    """Analyze text using tiktoken with numerical understanding"""
    
    def __init__(self, model: str = "gpt-3.5-turbo"):
        self.encoding = tiktoken.encoding_for_model(model)
        self.model = model
        
        logger.info(f"Initialized TiktokenNumericalAnalyzer for {model}")
    
    def tokenize(self, text: str) -> List[int]:
        """Tokenize text using tiktoken"""
        return self.encoding.encode(text)
    
    def detokenize(self, tokens: List[int]) -> str:
        """Convert tokens back to text"""
        return self.encoding.decode(tokens)
    
    def get_token_info(self, token_id: int) -> TokenInfo:
        """Get detailed information about a token"""
        token_str = self.encoding.decode([token_id])
        
        # Check if numerical
        is_numerical = self._is_numerical(token_str)
        numerical_value = self._extract_numerical_value(token_str) if is_numerical else None
        
        # Check if operator
        is_operator = token_str.strip() in ['+', '-', '*', '/', '%', '**', '//', '=', '==', '!=', '<', '>', '<=', '>=']
        
        # Check if punctuation
        is_punctuation = token_str.strip() in ['.', ',', '!', '?', ';', ':', '(', ')', '[', ']', '{', '}']
        
        return TokenInfo(
            token_id=token_id,
            token_str=token_str,
            is_numerical=is_numerical,
            numerical_value=numerical_value,
            is_operator=is_operator,
            is_punctuation=is_punctuation
        )
    
    def _is_numerical(self, token_str: str) -> bool:
        """Check if token is numerical"""
        token_clean = token_str.strip()
        
        # Check for numbers
        if re.match(r'^-?\d+\.?\d*$', token_clean):
            return True
        
        # Check for scientific notation
        if re.match(r'^-?\d+\.?\d*[eE][+-]?\d+$', token_clean):
            return True
        
        # Check for percentage
        if re.match(r'^-?\d+\.?\d*%$', token_clean):
            return True
        
        return False
    
    def _extract_numerical_value(self, token_str: str) -> Optional[float]:
        """Extract numerical value from token"""
        try:
            token_clean = token_str.strip()
            
            # Remove percentage sign
            if token_clean.endswith('%'):
                return float(token_clean[:-1]) / 100
            
            return float(token_clean)
        except:
            return None
    
    def analyze_sequence(self, text: str) -> Dict:
        """Analyze a sequence of tokens"""
        tokens = self.tokenize(text)
        
        analysis = {
            'text': text,
            'token_count': len(tokens),
            'tokens': tokens,
            'token_details': [self.get_token_info(t) for t in tokens],
            'numerical_tokens': [],
            'operator_tokens': [],
            'punctuation_tokens': [],
            'text_tokens': []
        }
        
        for info in analysis['token_details']:
            if info.is_numerical:
                analysis['numerical_tokens'].append((info.token_str, info.numerical_value))
            elif info.is_operator:
                analysis['operator_tokens'].append(info.token_str)
            elif info.is_punctuation:
                analysis['punctuation_tokens'].append(info.token_str)
            else:
                analysis['text_tokens'].append(info.token_str)
        
        return analysis


# ========== NUMERICAL CONTEXT UNDERSTANDING ==========

class NumericalContextUnderstanding:
    """Understand numerical context and patterns"""
    
    def __init__(self):
        self.numerical_patterns = defaultdict(list)
        self.sequence_patterns = defaultdict(list)
        
        logger.info("Initialized Numerical Context Understanding")
    
    def extract_numerical_context(self, text: str) -> Dict:
        """Extract numerical context from text"""
        # Extract all numbers
        numbers = re.findall(r'-?\d+\.?\d*', text)
        
        # Extract numerical expressions
        expressions = re.findall(r'\d+\s*[+\-*/%]\s*\d+', text)
        
        # Extract ranges
        ranges = re.findall(r'\d+\s*(?:to|-)\s*\d+', text)
        
        # Extract percentages
        percentages = re.findall(r'\d+\.?\d*%', text)
        
        context = {
            'numbers': [float(n) for n in numbers],
            'expressions': expressions,
            'ranges': ranges,
            'percentages': percentages,
            'statistics': self._compute_statistics([float(n) for n in numbers]) if numbers else {}
        }
        
        return context
    
    def _compute_statistics(self, numbers: List[float]) -> Dict:
        """Compute statistics on numbers"""
        if not numbers:
            return {}
        
        arr = np.array(numbers)
        
        return {
            'count': len(numbers),
            'sum': float(np.sum(arr)),
            'mean': float(np.mean(arr)),
            'median': float(np.median(arr)),
            'std': float(np.std(arr)),
            'min': float(np.min(arr)),
            'max': float(np.max(arr)),
            'range': float(np.max(arr) - np.min(arr))
        }
    
    def predict_next_number(self, numbers: List[float]) -> Tuple[float, float]:
        """
        Predict next number in sequence
        
        Returns:
            (predicted_number, confidence)
        """
        if len(numbers) < 2:
            return (numbers[-1] if numbers else 0, 0.3)
        
        # Check for arithmetic progression
        if self._is_arithmetic_progression(numbers):
            diff = numbers[-1] - numbers[-2]
            return (numbers[-1] + diff, 0.9)
        
        # Check for geometric progression
        if self._is_geometric_progression(numbers):
            ratio = numbers[-1] / numbers[-2] if numbers[-2] != 0 else 1
            return (numbers[-1] * ratio, 0.85)
        
        # Check for Fibonacci-like
        if len(numbers) >= 3 and numbers[-1] == numbers[-2] + numbers[-3]:
            return (numbers[-1] + numbers[-2], 0.8)
        
        # Default: linear extrapolation
        diff = np.mean(np.diff(numbers))
        return (numbers[-1] + diff, 0.6)
    
    def _is_arithmetic_progression(self, numbers: List[float], tolerance: float = 0.01) -> bool:
        """Check if sequence is arithmetic progression"""
        if len(numbers) < 2:
            return False
        
        diffs = np.diff(numbers)
        return np.std(diffs) < tolerance
    
    def _is_geometric_progression(self, numbers: List[float], tolerance: float = 0.01) -> bool:
        """Check if sequence is geometric progression"""
        if len(numbers) < 2 or any(n == 0 for n in numbers[:-1]):
            return False
        
        ratios = np.array(numbers[1:]) / np.array(numbers[:-1])
        return np.std(ratios) < tolerance


# ========== PROBABILITY DISTRIBUTION MODELING ==========

class TokenProbabilityDistribution:
    """Model probability distribution of tokens"""
    
    def __init__(self):
        self.token_frequencies = Counter()
        self.token_pairs = Counter()
        self.token_triplets = Counter()
        self.numerical_token_patterns = defaultdict(Counter)
        
        logger.info("Initialized Token Probability Distribution")
    
    def build_from_corpus(self, texts: List[str], tokenizer):
        """Build probability distribution from corpus"""
        logger.info(f"Building distribution from {len(texts)} texts")
        
        for text in texts:
            tokens = tokenizer.tokenize(text)
            
            # Count individual tokens
            self.token_frequencies.update(tokens)
            
            # Count pairs
            for i in range(len(tokens) - 1):
                self.token_pairs[(tokens[i], tokens[i+1])] += 1
            
            # Count triplets
            for i in range(len(tokens) - 2):
                self.token_triplets[(tokens[i], tokens[i+1], tokens[i+2])] += 1
    
    def get_token_probability(self, token_id: int) -> float:
        """Get probability of a token"""
        total = sum(self.token_frequencies.values())
        return self.token_frequencies[token_id] / total if total > 0 else 0
    
    def get_conditional_probability(self, prev_token: int, current_token: int) -> float:
        """Get P(current | previous)"""
        # Count occurrences of previous token
        prev_count = sum(1 for (p, c) in self.token_pairs if p == prev_token)
        
        if prev_count == 0:
            return self.get_token_probability(current_token)
        
        # Count co-occurrences
        co_occur = self.token_pairs[(prev_token, current_token)]
        
        return co_occur / prev_count if prev_count > 0 else 0
    
    def get_next_token_probabilities(self, prev_tokens: List[int], top_k: int = 10) -> List[Tuple[int, float]]:
        """Get probability distribution for next token"""
        if not prev_tokens:
            # Return most common tokens
            return [(token, self.get_token_probability(token)) 
                    for token, _ in self.token_frequencies.most_common(top_k)]
        
        last_token = prev_tokens[-1]
        
        # Find all tokens that follow last_token
        next_tokens = Counter()
        for (prev, next_t), count in self.token_pairs.items():
            if prev == last_token:
                next_tokens[next_t] = count
        
        if not next_tokens:
            # Fallback to most common tokens
            return [(token, self.get_token_probability(token)) 
                    for token, _ in self.token_frequencies.most_common(top_k)]
        
        # Normalize to probabilities
        total = sum(next_tokens.values())
        probabilities = [(token, count / total) for token, count in next_tokens.most_common(top_k)]
        
        return probabilities


# ========== ADVANCED TOKEN PREDICTION ==========

class AdvancedTokenPredictor:
    """Advanced token prediction with multiple strategies"""
    
    def __init__(self, model: str = "gpt-3.5-turbo"):
        self.tokenizer = TiktokenNumericalAnalyzer(model)
        self.context_analyzer = NumericalContextUnderstanding()
        self.probability_dist = TokenProbabilityDistribution()
        
        logger.info("Initialized Advanced Token Predictor")
    
    def predict_next_token(self, text: str, top_k: int = 5) -> PredictionResult:
        """
        Predict next token with high accuracy
        
        Args:
            text: Input text
            top_k: Number of top predictions
        
        Returns:
            PredictionResult with predictions and confidence
        """
        logger.info(f"Predicting next token for: '{text}'")
        
        # Tokenize
        tokens = self.tokenizer.tokenize(text)
        
        # Analyze sequence
        sequence_analysis = self.tokenizer.analyze_sequence(text)
        
        # Extract numerical context
        numerical_context = self.context_analyzer.extract_numerical_context(text)
        
        # Get token probabilities
        next_token_probs = self.probability_dist.get_next_token_probabilities(tokens, top_k=top_k)
        
        # Apply numerical reasoning if applicable
        reasoning = self._apply_reasoning(sequence_analysis, numerical_context)
        
        # Get top prediction
        if next_token_probs:
            top_token_id, top_prob = next_token_probs[0]
            top_token_str = self.tokenizer.encoding.decode([top_token_id])
        else:
            top_token_id, top_prob = 0, 0
            top_token_str = ""
        
        # Calculate confidence
        confidence = self._calculate_confidence(top_prob, sequence_analysis, numerical_context)
        
        # Prepare top 5
        top_5 = [(self.tokenizer.encoding.decode([tid]), prob) for tid, prob in next_token_probs[:5]]
        
        return PredictionResult(
            input_text=text,
            input_tokens=tokens,
            predicted_token=top_token_str,
            predicted_token_id=top_token_id,
            probability=top_prob,
            confidence=confidence,
            top_5_predictions=top_5,
            reasoning=reasoning
        )
    
    def _apply_reasoning(self, sequence_analysis: Dict, numerical_context: Dict) -> str:
        """Apply reasoning to improve prediction"""
        reasoning = []
        
        # Numerical reasoning
        if numerical_context['numbers']:
            reasoning.append(f"Numerical context detected: {len(numerical_context['numbers'])} numbers")
            
            # Predict next number if applicable
            if len(numerical_context['numbers']) >= 2:
                next_num, confidence = self.context_analyzer.predict_next_number(numerical_context['numbers'])
                reasoning.append(f"Predicted next number: {next_num:.2f} (confidence: {confidence:.1%})")
        
        # Pattern reasoning
        if sequence_analysis['numerical_tokens']:
            reasoning.append(f"Numerical tokens: {len(sequence_analysis['numerical_tokens'])}")
        
        if sequence_analysis['operator_tokens']:
            reasoning.append(f"Operators: {sequence_analysis['operator_tokens']}")
        
        return " | ".join(reasoning) if reasoning else "No special reasoning applied"
    
    def _calculate_confidence(self, probability: float, sequence_analysis: Dict, numerical_context: Dict) -> float:
        """Calculate confidence score"""
        confidence = probability
        
        # Boost confidence for numerical patterns
        if numerical_context['numbers'] and len(numerical_context['numbers']) >= 2:
            confidence *= 1.2
        
        # Boost confidence for clear patterns
        if sequence_analysis['operator_tokens']:
            confidence *= 1.1
        
        # Cap at 1.0
        return min(confidence, 1.0)
    
    def predict_with_context(self, text: str, context_length: int = 5) -> List[PredictionResult]:
        """
        Predict multiple tokens ahead
        
        Args:
            text: Input text
            context_length: Number of tokens to predict
        
        Returns:
            List of predictions
        """
        predictions = []
        current_text = text
        
        for i in range(context_length):
            prediction = self.predict_next_token(current_text)
            predictions.append(prediction)
            
            # Add predicted token to text
            current_text += prediction.predicted_token
        
        return predictions


# ========== STATISTICAL ANALYSIS ==========

class StatisticalAnalyzer:
    """Statistical analysis of token patterns"""
    
    def __init__(self, tokenizer):
        self.tokenizer = tokenizer
        
        logger.info("Initialized Statistical Analyzer")
    
    def analyze_token_distribution(self, texts: List[str]) -> Dict:
        """Analyze distribution of tokens"""
        all_tokens = []
        
        for text in texts:
            tokens = self.tokenizer.tokenize(text)
            all_tokens.extend(tokens)
        
        token_freq = Counter(all_tokens)
        
        return {
            'total_tokens': len(all_tokens),
            'unique_tokens': len(token_freq),
            'most_common': token_freq.most_common(10),
            'entropy': self._calculate_entropy(token_freq),
            'diversity': len(token_freq) / len(all_tokens) if all_tokens else 0
        }
    
    def _calculate_entropy(self, token_freq: Counter) -> float:
        """Calculate Shannon entropy"""
        total = sum(token_freq.values())
        entropy = 0
        
        for count in token_freq.values():
            p = count / total
            if p > 0:
                entropy -= p * math.log2(p)
        
        return entropy
    
    def analyze_numerical_patterns(self, texts: List[str]) -> Dict:
        """Analyze numerical patterns in texts"""
        all_numbers = []
        
        for text in texts:
            numbers = re.findall(r'-?\d+\.?\d*', text)
            all_numbers.extend([float(n) for n in numbers])
        
        if not all_numbers:
            return {'error': 'No numbers found'}
        
        arr = np.array(all_numbers)
        
        return {
            'count': len(all_numbers),
            'unique': len(set(all_numbers)),
            'sum': float(np.sum(arr)),
            'mean': float(np.mean(arr)),
            'median': float(np.median(arr)),
            'std': float(np.std(arr)),
            'min': float(np.min(arr)),
            'max': float(np.max(arr)),
            'distribution': self._analyze_distribution(all_numbers)
        }
    
    def _analyze_distribution(self, numbers: List[float]) -> Dict:
        """Analyze distribution type"""
        arr = np.array(numbers)
        
        # Check for normal distribution (simplified)
        skewness = (np.mean(arr) - np.median(arr)) / (np.std(arr) + 1e-10)
        
        if abs(skewness) < 0.5:
            dist_type = "approximately normal"
        elif skewness > 0:
            dist_type = "right-skewed"
        else:
            dist_type = "left-skewed"
        
        return {
            'type': dist_type,
            'skewness': float(skewness),
            'kurtosis': float(self._calculate_kurtosis(arr))
        }
    
    def _calculate_kurtosis(self, arr: np.ndarray) -> float:
        """Calculate kurtosis"""
        n = len(arr)
        mean = np.mean(arr)
        std = np.std(arr)
        
        if std == 0:
            return 0
        
        return np.sum(((arr - mean) / std) ** 4) / n - 3


# ========== MAIN ==========

def main():
    """Example usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Advanced Numerical Token Predictor")
    parser.add_argument("--text", default="The sum of 2 + 3 is", help="Input text")
    parser.add_argument("--model", default="gpt-3.5-turbo", help="Model name")
    parser.add_argument("--top-k", type=int, default=5, help="Top K predictions")
    parser.add_argument("--context-length", type=int, default=1, help="Context length")
    
    args = parser.parse_args()
    
    # Initialize predictor
    predictor = AdvancedTokenPredictor(model=args.model)
    
    # Make prediction
    logger.info(f"Input: '{args.text}'")
    
    if args.context_length == 1:
        result = predictor.predict_next_token(args.text, top_k=args.top_k)
        
        print("\n" + "="*80)
        print("ADVANCED NUMERICAL TOKEN PREDICTION")
        print("="*80)
        print(f"Input text: {result.input_text}")
        print(f"Predicted token: '{result.predicted_token}'")
        print(f"Probability: {result.probability:.4f}")
        print(f"Confidence: {result.confidence:.1%}")
        print(f"\nReasoning: {result.reasoning}")
        print(f"\nTop {args.top_k} predictions:")
        for i, (token, prob) in enumerate(result.top_5_predictions, 1):
            print(f"  {i}. '{token}' - {prob:.4f}")
        print("="*80)
    else:
        results = predictor.predict_with_context(args.text, context_length=args.context_length)
        
        print("\n" + "="*80)
        print("MULTI-TOKEN PREDICTION")
        print("="*80)
        print(f"Input: '{args.text}'")
        print(f"\nPredicting {args.context_length} tokens ahead:\n")
        
        for i, result in enumerate(results, 1):
            print(f"Token {i}: '{result.predicted_token}' (prob: {result.probability:.4f}, conf: {result.confidence:.1%})")
        
        print("="*80)


if __name__ == "__main__":
    main()
