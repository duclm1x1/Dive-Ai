#!/usr/bin/env python3
"""
State-of-the-Art Next-Word Prediction Models
Multiple base models with ensemble methods for highest accuracy
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from transformers import (
    AutoTokenizer, AutoModelForCausalLM,
    GPT2LMHeadModel, GPT2Tokenizer,
    DistilBertTokenizer, DistilBertModel
)
import tiktoken
import numpy as np
from typing import Dict, List, Tuple, Optional
import logging
from collections import Counter, defaultdict
from dataclasses import dataclass
import json
from datetime import datetime
import pickle

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ========== DATA STRUCTURES ==========

@dataclass
class PredictionResult:
    """Result of next-word prediction"""
    input_text: str
    predicted_word: str
    predicted_token_id: int
    probability: float
    confidence: float
    top_5: List[Tuple[str, float]]
    model_name: str
    timestamp: str


@dataclass
class EnsembleResult:
    """Result from ensemble prediction"""
    input_text: str
    predicted_word: str
    probability: float
    confidence: float
    top_5: List[Tuple[str, float]]
    model_votes: Dict[str, str]
    ensemble_method: str
    timestamp: str


# ========== BASE MODELS ==========

class BaseModel:
    """Base class for next-word prediction models"""
    
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        logger.info(f"Initializing {model_name} on {self.device}")
    
    def predict(self, text: str, top_k: int = 5) -> PredictionResult:
        raise NotImplementedError
    
    def batch_predict(self, texts: List[str], top_k: int = 5) -> List[PredictionResult]:
        raise NotImplementedError


class GPT2Model(BaseModel):
    """GPT-2 based next-word predictor"""
    
    def __init__(self):
        super().__init__("gpt2")
        
        self.tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
        self.model = GPT2LMHeadModel.from_pretrained("gpt2").to(self.device)
        self.model.eval()
        
        logger.info("GPT-2 model loaded")
    
    def predict(self, text: str, top_k: int = 5) -> PredictionResult:
        """Predict next word using GPT-2"""
        with torch.no_grad():
            # Tokenize
            inputs = self.tokenizer.encode(text, return_tensors="pt").to(self.device)
            
            # Get logits
            outputs = self.model(inputs)
            logits = outputs.logits[0, -1, :]
            
            # Get top-k
            top_probs, top_indices = torch.topk(F.softmax(logits, dim=-1), top_k)
            
            # Decode
            top_words = [self.tokenizer.decode([idx.item()]) for idx in top_indices]
            top_probs = top_probs.cpu().numpy().tolist()
            
            return PredictionResult(
                input_text=text,
                predicted_word=top_words[0],
                predicted_token_id=top_indices[0].item(),
                probability=top_probs[0],
                confidence=top_probs[0],
                top_5=list(zip(top_words, top_probs)),
                model_name="gpt2",
                timestamp=datetime.now().isoformat()
            )


class DistilGPT2Model(BaseModel):
    """DistilGPT-2 based predictor (faster)"""
    
    def __init__(self):
        super().__init__("distilgpt2")
        
        self.tokenizer = AutoTokenizer.from_pretrained("distilgpt2")
        self.model = AutoModelForCausalLM.from_pretrained("distilgpt2").to(self.device)
        self.model.eval()
        
        logger.info("DistilGPT-2 model loaded")
    
    def predict(self, text: str, top_k: int = 5) -> PredictionResult:
        """Predict next word using DistilGPT-2"""
        with torch.no_grad():
            inputs = self.tokenizer.encode(text, return_tensors="pt").to(self.device)
            outputs = self.model(inputs)
            logits = outputs.logits[0, -1, :]
            
            top_probs, top_indices = torch.topk(F.softmax(logits, dim=-1), top_k)
            top_words = [self.tokenizer.decode([idx.item()]) for idx in top_indices]
            top_probs = top_probs.cpu().numpy().tolist()
            
            return PredictionResult(
                input_text=text,
                predicted_word=top_words[0],
                predicted_token_id=top_indices[0].item(),
                probability=top_probs[0],
                confidence=top_probs[0],
                top_5=list(zip(top_words, top_probs)),
                model_name="distilgpt2",
                timestamp=datetime.now().isoformat()
            )


class TiktokenModel(BaseModel):
    """Tiktoken-based statistical model"""
    
    def __init__(self):
        super().__init__("tiktoken-statistical")
        
        self.encoding = tiktoken.get_encoding("cl100k_base")
        self.token_pairs = Counter()
        self.token_freq = Counter()
        
        logger.info("Tiktoken statistical model initialized")
    
    def train_on_corpus(self, texts: List[str]):
        """Train on corpus"""
        logger.info(f"Training on {len(texts)} texts")
        
        for text in texts:
            tokens = self.encoding.encode(text)
            self.token_freq.update(tokens)
            
            for i in range(len(tokens) - 1):
                self.token_pairs[(tokens[i], tokens[i+1])] += 1
    
    def predict(self, text: str, top_k: int = 5) -> PredictionResult:
        """Predict next word using statistical model"""
        tokens = self.encoding.encode(text)
        
        if not tokens:
            return PredictionResult(
                input_text=text,
                predicted_word="",
                predicted_token_id=0,
                probability=0,
                confidence=0,
                top_5=[],
                model_name="tiktoken-statistical",
                timestamp=datetime.now().isoformat()
            )
        
        last_token = tokens[-1]
        
        # Find next tokens
        next_tokens = Counter()
        for (prev, next_t), count in self.token_pairs.items():
            if prev == last_token:
                next_tokens[next_t] = count
        
        if not next_tokens:
            return PredictionResult(
                input_text=text,
                predicted_word="",
                predicted_token_id=0,
                probability=0,
                confidence=0,
                top_5=[],
                model_name="tiktoken-statistical",
                timestamp=datetime.now().isoformat()
            )
        
        # Get top-k
        total = sum(next_tokens.values())
        top_predictions = next_tokens.most_common(top_k)
        
        top_words = [self.encoding.decode([token_id]) for token_id, _ in top_predictions]
        top_probs = [count / total for _, count in top_predictions]
        
        return PredictionResult(
            input_text=text,
            predicted_word=top_words[0],
            predicted_token_id=top_predictions[0][0],
            probability=top_probs[0],
            confidence=top_probs[0],
            top_5=list(zip(top_words, top_probs)),
            model_name="tiktoken-statistical",
            timestamp=datetime.now().isoformat()
        )


class HybridModel(BaseModel):
    """Hybrid model combining multiple approaches"""
    
    def __init__(self):
        super().__init__("hybrid")
        
        self.gpt2 = GPT2Model()
        self.distilgpt2 = DistilGPT2Model()
        self.tiktoken_enc = tiktoken.get_encoding("cl100k_base")
        
        logger.info("Hybrid model initialized")
    
    def predict(self, text: str, top_k: int = 5) -> PredictionResult:
        """Predict using hybrid approach"""
        # Get predictions from both models
        gpt2_result = self.gpt2.predict(text, top_k)
        distil_result = self.distilgpt2.predict(text, top_k)
        
        # Average probabilities
        combined_probs = defaultdict(float)
        
        for word, prob in gpt2_result.top_5:
            combined_probs[word] += prob * 0.5
        
        for word, prob in distil_result.top_5:
            combined_probs[word] += prob * 0.5
        
        # Sort by probability
        sorted_predictions = sorted(combined_probs.items(), key=lambda x: x[1], reverse=True)[:top_k]
        
        return PredictionResult(
            input_text=text,
            predicted_word=sorted_predictions[0][0],
            predicted_token_id=0,
            probability=sorted_predictions[0][1],
            confidence=sorted_predictions[0][1],
            top_5=sorted_predictions,
            model_name="hybrid",
            timestamp=datetime.now().isoformat()
        )


# ========== ENSEMBLE PREDICTOR ==========

class EnsemblePredictor:
    """Ensemble of multiple models for highest accuracy"""
    
    def __init__(self, use_gpt2: bool = True, use_distilgpt2: bool = True):
        self.models = {}
        
        if use_gpt2:
            try:
                self.models['gpt2'] = GPT2Model()
            except Exception as e:
                logger.warning(f"Failed to load GPT-2: {e}")
        
        if use_distilgpt2:
            try:
                self.models['distilgpt2'] = DistilGPT2Model()
            except Exception as e:
                logger.warning(f"Failed to load DistilGPT-2: {e}")
        
        # Add hybrid model
        if len(self.models) > 1:
            self.models['hybrid'] = HybridModel()
        
        logger.info(f"Ensemble initialized with {len(self.models)} models")
    
    def predict_voting(self, text: str, top_k: int = 5) -> EnsembleResult:
        """Predict using voting ensemble"""
        predictions = {}
        votes = Counter()
        
        for model_name, model in self.models.items():
            result = model.predict(text, top_k=1)
            predictions[model_name] = result
            votes[result.predicted_word] += 1
        
        # Get consensus prediction
        consensus_word = votes.most_common(1)[0][0]
        
        # Average probabilities
        avg_probs = defaultdict(float)
        for model_name, result in predictions.items():
            for word, prob in result.top_5:
                avg_probs[word] += prob / len(self.models)
        
        sorted_predictions = sorted(avg_probs.items(), key=lambda x: x[1], reverse=True)[:top_k]
        
        return EnsembleResult(
            input_text=text,
            predicted_word=consensus_word,
            probability=avg_probs[consensus_word],
            confidence=votes[consensus_word] / len(self.models),
            top_5=sorted_predictions,
            model_votes={m: p.predicted_word for m, p in predictions.items()},
            ensemble_method="voting",
            timestamp=datetime.now().isoformat()
        )
    
    def predict_averaging(self, text: str, top_k: int = 5) -> EnsembleResult:
        """Predict using probability averaging"""
        avg_probs = defaultdict(float)
        model_votes = {}
        
        for model_name, model in self.models.items():
            result = model.predict(text, top_k=top_k)
            model_votes[model_name] = result.predicted_word
            
            for word, prob in result.top_5:
                avg_probs[word] += prob / len(self.models)
        
        sorted_predictions = sorted(avg_probs.items(), key=lambda x: x[1], reverse=True)[:top_k]
        
        return EnsembleResult(
            input_text=text,
            predicted_word=sorted_predictions[0][0],
            probability=sorted_predictions[0][1],
            confidence=sorted_predictions[0][1],
            top_5=sorted_predictions,
            model_votes=model_votes,
            ensemble_method="averaging",
            timestamp=datetime.now().isoformat()
        )
    
    def predict_weighted(self, text: str, top_k: int = 5, weights: Optional[Dict] = None) -> EnsembleResult:
        """Predict using weighted ensemble"""
        if weights is None:
            weights = {name: 1.0 / len(self.models) for name in self.models}
        
        avg_probs = defaultdict(float)
        model_votes = {}
        
        for model_name, model in self.models.items():
            result = model.predict(text, top_k=top_k)
            model_votes[model_name] = result.predicted_word
            weight = weights.get(model_name, 1.0 / len(self.models))
            
            for word, prob in result.top_5:
                avg_probs[word] += prob * weight
        
        sorted_predictions = sorted(avg_probs.items(), key=lambda x: x[1], reverse=True)[:top_k]
        
        return EnsembleResult(
            input_text=text,
            predicted_word=sorted_predictions[0][0],
            probability=sorted_predictions[0][1],
            confidence=sorted_predictions[0][1],
            top_5=sorted_predictions,
            model_votes=model_votes,
            ensemble_method="weighted",
            timestamp=datetime.now().isoformat()
        )


# ========== EVALUATION ==========

class NextWordEvaluator:
    """Evaluate next-word prediction accuracy"""
    
    def __init__(self):
        self.results = []
        
        logger.info("Initialized Next-Word Evaluator")
    
    def evaluate_on_corpus(self, texts: List[str], predictor, top_k: int = 5) -> Dict:
        """Evaluate on corpus"""
        logger.info(f"Evaluating on {len(texts)} texts")
        
        correct_top1 = 0
        correct_top5 = 0
        total = 0
        
        for text in texts:
            # Split into context and target
            words = text.split()
            if len(words) < 2:
                continue
            
            context = " ".join(words[:-1])
            target = words[-1].lower()
            
            # Get prediction
            if isinstance(predictor, EnsemblePredictor):
                result = predictor.predict_averaging(context, top_k=top_k)
                predicted = result.predicted_word.lower().strip()
                top_5_words = [w.lower().strip() for w, _ in result.top_5]
            else:
                result = predictor.predict(context, top_k=top_k)
                predicted = result.predicted_word.lower().strip()
                top_5_words = [w.lower().strip() for w, _ in result.top_5]
            
            # Check accuracy
            if predicted == target:
                correct_top1 += 1
            
            if target in top_5_words:
                correct_top5 += 1
            
            total += 1
        
        return {
            'total': total,
            'top1_accuracy': correct_top1 / total if total > 0 else 0,
            'top5_accuracy': correct_top5 / total if total > 0 else 0,
            'top1_count': correct_top1,
            'top5_count': correct_top5
        }
    
    def evaluate_perplexity(self, texts: List[str], model) -> float:
        """Evaluate perplexity"""
        total_loss = 0
        total_tokens = 0
        
        for text in texts:
            words = text.split()
            for i in range(1, len(words)):
                context = " ".join(words[:i])
                target = words[i]
                
                result = model.predict(context, top_k=1)
                
                # Find probability of target word
                target_prob = 0
                for word, prob in result.top_5:
                    if word.lower().strip() == target.lower():
                        target_prob = prob
                        break
                
                if target_prob > 0:
                    total_loss += -np.log(target_prob)
                else:
                    total_loss += -np.log(1e-10)
                
                total_tokens += 1
        
        perplexity = np.exp(total_loss / total_tokens) if total_tokens > 0 else float('inf')
        return perplexity


# ========== MAIN ==========

def main():
    """Example usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="State-of-the-Art Next-Word Prediction")
    parser.add_argument("--text", default="The quick brown fox jumps over the", help="Input text")
    parser.add_argument("--model", choices=["gpt2", "distilgpt2", "ensemble"], default="ensemble", help="Model to use")
    parser.add_argument("--top-k", type=int, default=5, help="Top K predictions")
    
    args = parser.parse_args()
    
    logger.info(f"Input: '{args.text}'")
    
    if args.model == "gpt2":
        model = GPT2Model()
        result = model.predict(args.text, top_k=args.top_k)
    elif args.model == "distilgpt2":
        model = DistilGPT2Model()
        result = model.predict(args.text, top_k=args.top_k)
    else:
        ensemble = EnsemblePredictor()
        result = ensemble.predict_averaging(args.text, top_k=args.top_k)
    
    print("\n" + "="*80)
    print("NEXT-WORD PREDICTION RESULT")
    print("="*80)
    print(f"Input: '{args.text}'")
    print(f"Predicted word: '{result.predicted_word}'")
    print(f"Probability: {result.probability:.4f}")
    print(f"Confidence: {result.confidence:.1%}")
    print(f"\nTop {args.top_k} predictions:")
    for i, (word, prob) in enumerate(result.top_5, 1):
        print(f"  {i}. '{word}' - {prob:.4f}")
    print("="*80)


if __name__ == "__main__":
    main()
