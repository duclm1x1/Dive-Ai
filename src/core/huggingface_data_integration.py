#!/usr/bin/env python3
"""
Hugging Face Data Integration for Future Language Prediction
Fetches linguistic data, analyzes trends, and predicts language evolution 20 years ahead
"""

import os
from datasets import load_dataset, DatasetDict
from transformers import AutoTokenizer, AutoModelForCausalLM
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import json
import logging
from collections import Counter, defaultdict
import re
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ========== HUGGING FACE DATA LOADER ==========

class HuggingFaceDataLoader:
    """Load and manage datasets from Hugging Face"""
    
    def __init__(self, cache_dir: str = "/home/ubuntu/hf_datasets"):
        self.cache_dir = cache_dir
        Path(cache_dir).mkdir(parents=True, exist_ok=True)
        self.datasets = {}
        
        logger.info(f"Initialized HF Data Loader - Cache: {cache_dir}")
    
    def load_wikitext(self, version: str = "wikitext-103-v1") -> DatasetDict:
        """Load WikiText dataset for historical text analysis"""
        logger.info(f"Loading WikiText dataset: {version}")
        
        try:
            dataset = load_dataset(
                "wikitext",
                version.split("-")[1].lower(),
                cache_dir=self.cache_dir
            )
            self.datasets['wikitext'] = dataset
            logger.info(f"WikiText loaded - Splits: {list(dataset.keys())}")
            return dataset
        except Exception as e:
            logger.error(f"Error loading WikiText: {e}")
            return None
    
    def load_common_crawl(self) -> DatasetDict:
        """Load Common Crawl dataset for web text analysis"""
        logger.info("Loading Common Crawl dataset")
        
        try:
            dataset = load_dataset(
                "common_crawl",
                "2021-04",
                cache_dir=self.cache_dir,
                split="train[:1%]"  # Load 1% for efficiency
            )
            self.datasets['common_crawl'] = dataset
            logger.info(f"Common Crawl loaded - Samples: {len(dataset)}")
            return dataset
        except Exception as e:
            logger.error(f"Error loading Common Crawl: {e}")
            return None
    
    def load_news_dataset(self) -> DatasetDict:
        """Load news dataset for recent language trends"""
        logger.info("Loading News dataset")
        
        try:
            dataset = load_dataset(
                "ag_news",
                cache_dir=self.cache_dir
            )
            self.datasets['news'] = dataset
            logger.info(f"News dataset loaded - Splits: {list(dataset.keys())}")
            return dataset
        except Exception as e:
            logger.error(f"Error loading News dataset: {e}")
            return None
    
    def load_social_media_dataset(self) -> DatasetDict:
        """Load social media dataset for modern language trends"""
        logger.info("Loading Social Media dataset")
        
        try:
            dataset = load_dataset(
                "tweet_eval",
                "sentiment",
                cache_dir=self.cache_dir,
                split="train[:10000]"
            )
            self.datasets['social_media'] = dataset
            logger.info(f"Social Media dataset loaded - Samples: {len(dataset)}")
            return dataset
        except Exception as e:
            logger.error(f"Error loading Social Media dataset: {e}")
            return None
    
    def load_code_dataset(self) -> DatasetDict:
        """Load code dataset for tech language trends"""
        logger.info("Loading Code dataset")
        
        try:
            dataset = load_dataset(
                "codeparrot/github-code",
                languages=["Python"],
                cache_dir=self.cache_dir,
                split="train[:5000]"
            )
            self.datasets['code'] = dataset
            logger.info(f"Code dataset loaded - Samples: {len(dataset)}")
            return dataset
        except Exception as e:
            logger.error(f"Error loading Code dataset: {e}")
            return None
    
    def load_multilingual_dataset(self) -> DatasetDict:
        """Load multilingual dataset for language evolution"""
        logger.info("Loading Multilingual dataset")
        
        try:
            dataset = load_dataset(
                "wmt14",
                "de-en",
                cache_dir=self.cache_dir,
                split="train[:10000]"
            )
            self.datasets['multilingual'] = dataset
            logger.info(f"Multilingual dataset loaded - Samples: {len(dataset)}")
            return dataset
        except Exception as e:
            logger.error(f"Error loading Multilingual dataset: {e}")
            return None
    
    def load_all_datasets(self) -> Dict:
        """Load all available datasets"""
        logger.info("Loading all datasets...")
        
        datasets = {}
        
        # Load each dataset
        if wikitext := self.load_wikitext():
            datasets['wikitext'] = wikitext
        
        if news := self.load_news_dataset():
            datasets['news'] = news
        
        if social := self.load_social_media_dataset():
            datasets['social_media'] = social
        
        if code := self.load_code_dataset():
            datasets['code'] = code
        
        logger.info(f"Loaded {len(datasets)} datasets")
        return datasets


# ========== LINGUISTIC ANALYSIS ==========

class LinguisticAnalyzer:
    """Analyze linguistic patterns and trends"""
    
    def __init__(self):
        self.word_freq_history = defaultdict(list)
        self.ngram_freq_history = defaultdict(list)
        self.semantic_shifts = {}
        self.neologisms = []
        
        logger.info("Initialized Linguistic Analyzer")
    
    def extract_vocabulary(self, texts: List[str]) -> Dict[str, int]:
        """Extract and count vocabulary"""
        logger.info(f"Extracting vocabulary from {len(texts)} texts")
        
        vocab = Counter()
        
        for text in texts:
            # Tokenize and clean
            words = re.findall(r'\b\w+\b', text.lower())
            vocab.update(words)
        
        logger.info(f"Extracted {len(vocab)} unique words")
        return dict(vocab)
    
    def extract_ngrams(self, texts: List[str], n: int = 2) -> Dict[str, int]:
        """Extract n-grams"""
        logger.info(f"Extracting {n}-grams from {len(texts)} texts")
        
        ngrams = Counter()
        
        for text in texts:
            words = re.findall(r'\b\w+\b', text.lower())
            for i in range(len(words) - n + 1):
                ngram = ' '.join(words[i:i+n])
                ngrams[ngram] += 1
        
        logger.info(f"Extracted {len(ngrams)} unique {n}-grams")
        return dict(ngrams)
    
    def analyze_trends(self, historical_data: Dict[str, List]) -> Dict:
        """Analyze linguistic trends over time"""
        logger.info("Analyzing linguistic trends")
        
        trends = {
            'emerging_words': [],
            'declining_words': [],
            'stable_words': [],
            'growth_rate': {},
            'decline_rate': {}
        }
        
        for word, frequencies in historical_data.items():
            if len(frequencies) < 2:
                continue
            
            # Calculate trend
            early_freq = np.mean(frequencies[:len(frequencies)//2])
            recent_freq = np.mean(frequencies[len(frequencies)//2:])
            
            if early_freq == 0:
                growth_rate = float('inf') if recent_freq > 0 else 0
            else:
                growth_rate = (recent_freq - early_freq) / early_freq
            
            # Classify
            if growth_rate > 0.5:
                trends['emerging_words'].append((word, growth_rate))
            elif growth_rate < -0.5:
                trends['declining_words'].append((word, growth_rate))
            else:
                trends['stable_words'].append((word, growth_rate))
            
            trends['growth_rate'][word] = growth_rate
        
        # Sort by growth rate
        trends['emerging_words'].sort(key=lambda x: x[1], reverse=True)
        trends['declining_words'].sort(key=lambda x: x[1])
        
        logger.info(f"Emerging words: {len(trends['emerging_words'])}")
        logger.info(f"Declining words: {len(trends['declining_words'])}")
        
        return trends
    
    def detect_semantic_shifts(self, word: str, contexts_past: List[str], contexts_present: List[str]) -> Dict:
        """Detect semantic shifts in word meaning"""
        logger.info(f"Detecting semantic shift for '{word}'")
        
        # Extract context words
        def get_context_words(contexts, window=5):
            context_vocab = Counter()
            for context in contexts:
                words = re.findall(r'\b\w+\b', context.lower())
                # Get surrounding words
                for i, w in enumerate(words):
                    if w == word:
                        start = max(0, i - window)
                        end = min(len(words), i + window + 1)
                        context_vocab.update(words[start:end])
            return context_vocab
        
        past_context = get_context_words(contexts_past)
        present_context = get_context_words(contexts_present)
        
        # Calculate shift
        shift = {
            'word': word,
            'past_context': dict(past_context.most_common(10)),
            'present_context': dict(present_context.most_common(10)),
            'context_shift': len(set(past_context.keys()) - set(present_context.keys()))
        }
        
        return shift
    
    def identify_neologisms(self, texts: List[str], reference_vocab: set) -> List[str]:
        """Identify new words (neologisms)"""
        logger.info("Identifying neologisms")
        
        neologisms = []
        
        for text in texts:
            words = re.findall(r'\b\w+\b', text.lower())
            for word in words:
                if word not in reference_vocab and len(word) > 3:
                    neologisms.append(word)
        
        # Count occurrences
        neologism_freq = Counter(neologisms)
        
        # Filter by frequency
        frequent_neologisms = [word for word, freq in neologism_freq.most_common(100) if freq > 2]
        
        logger.info(f"Identified {len(frequent_neologisms)} neologisms")
        return frequent_neologisms


# ========== FUTURE PREDICTION ==========

class FutureLanguagePredictor:
    """Predict language evolution 20 years into the future"""
    
    def __init__(self, years_ahead: int = 20):
        self.years_ahead = years_ahead
        self.target_year = datetime.now().year + years_ahead
        
        logger.info(f"Initialized Future Language Predictor - Target year: {self.target_year}")
    
    def extrapolate_trends(self, trends: Dict, historical_years: int = 10) -> Dict:
        """Extrapolate current trends to future"""
        logger.info(f"Extrapolating trends {self.years_ahead} years ahead")
        
        future_predictions = {
            'emerging_in_future': [],
            'declining_in_future': [],
            'new_words': [],
            'obsolete_words': []
        }
        
        # Extrapolate emerging words
        for word, growth_rate in trends['emerging_words'][:50]:
            # Exponential growth model
            future_growth = growth_rate ** (self.years_ahead / historical_years)
            
            if future_growth > 2.0:
                future_predictions['emerging_in_future'].append({
                    'word': word,
                    'current_growth': growth_rate,
                    'projected_growth': future_growth,
                    'confidence': min(future_growth / 5, 1.0)
                })
        
        # Extrapolate declining words
        for word, decline_rate in trends['declining_words'][:50]:
            future_decline = decline_rate ** (self.years_ahead / historical_years)
            
            if future_decline < -0.5:
                future_predictions['declining_in_future'].append({
                    'word': word,
                    'current_decline': decline_rate,
                    'projected_decline': future_decline,
                    'confidence': min(abs(future_decline) / 2, 1.0)
                })
        
        return future_predictions
    
    def predict_neologisms(self, current_neologisms: List[str], tech_trends: List[str]) -> List[Dict]:
        """Predict new words that will emerge"""
        logger.info("Predicting future neologisms")
        
        predictions = []
        
        # Tech-influenced neologisms
        tech_prefixes = ['cyber', 'bio', 'neuro', 'quantum', 'meta', 'ai', 'web3']
        tech_suffixes = ['-ify', '-ization', '-bot', '-tech', '-verse']
        
        for prefix in tech_prefixes:
            for suffix in tech_suffixes:
                neologism = prefix + suffix
                predictions.append({
                    'word': neologism,
                    'type': 'tech_influenced',
                    'probability': 0.6,
                    'emergence_year': self.target_year - np.random.randint(0, 5)
                })
        
        # Semantic shifts creating new meanings
        for word in current_neologisms[:20]:
            predictions.append({
                'word': word,
                'type': 'semantic_evolution',
                'probability': 0.4,
                'emergence_year': self.target_year
            })
        
        return predictions
    
    def predict_language_features(self) -> Dict:
        """Predict language features in 20 years"""
        logger.info(f"Predicting language features for {self.target_year}")
        
        predictions = {
            'year': self.target_year,
            'vocabulary_size_growth': 1.3,  # 30% growth
            'abbreviation_prevalence': 0.7,  # More abbreviations
            'emoji_integration': 0.8,  # More emoji use
            'multilingual_code_switching': 0.6,  # More code-switching
            'ai_influenced_language': 0.9,  # Heavy AI influence
            'formality_decline': 0.7,  # Less formal language
            'speed_increase': 0.8,  # Faster communication
            'personalization_level': 0.85,  # Highly personalized
        }
        
        return predictions


# ========== INTEGRATION WITH CHATGPT ==========

class ChatGPTNextWordPredictor:
    """Use ChatGPT API for next-word prediction"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        
        if not self.api_key:
            logger.warning("OPENAI_API_KEY not set")
        
        logger.info("Initialized ChatGPT Next-Word Predictor")
    
    def predict_next_word(self, text: str, num_predictions: int = 5) -> List[str]:
        """Predict next word using ChatGPT"""
        logger.info(f"Predicting next word for: '{text}'")
        
        try:
            from openai import OpenAI
            
            client = OpenAI(api_key=self.api_key)
            
            prompt = f"""Given this text: "{text}"
            
Predict the 5 most likely next words, ranked by probability.
Format: word1, word2, word3, word4, word5"""
            
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=100
            )
            
            predictions = response.choices[0].message.content.strip().split(", ")
            
            logger.info(f"Predictions: {predictions}")
            return predictions
        
        except Exception as e:
            logger.error(f"Error with ChatGPT API: {e}")
            return []
    
    def predict_future_language(self, text: str, years_ahead: int = 20) -> Dict:
        """Predict how text would be written in the future"""
        logger.info(f"Predicting future language ({years_ahead} years ahead)")
        
        try:
            from openai import OpenAI
            
            client = OpenAI(api_key=self.api_key)
            
            prompt = f"""Given this text from 2024: "{text}"
            
How would this be written in {2024 + years_ahead}? Consider:
1. New slang and abbreviations
2. AI-influenced language
3. Emoji and symbol integration
4. Semantic shifts
5. New technologies mentioned

Provide the predicted text and explain the changes."""
            
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.8,
                max_tokens=300
            )
            
            prediction = response.choices[0].message.content
            
            return {
                'original_text': text,
                'target_year': 2024 + years_ahead,
                'predicted_text': prediction
            }
        
        except Exception as e:
            logger.error(f"Error with ChatGPT API: {e}")
            return {}


# ========== MAIN INTEGRATION ==========

class FutureLanguagePredictionSystem:
    """Complete system for future language prediction"""
    
    def __init__(self):
        self.data_loader = HuggingFaceDataLoader()
        self.analyzer = LinguisticAnalyzer()
        self.predictor = FutureLanguagePredictor(years_ahead=20)
        self.chatgpt_predictor = ChatGPTNextWordPredictor()
        
        logger.info("Initialized Future Language Prediction System")
    
    def run_full_analysis(self) -> Dict:
        """Run complete analysis pipeline"""
        logger.info("Starting full analysis pipeline")
        
        # 1. Load datasets
        logger.info("Phase 1: Loading datasets from Hugging Face")
        datasets = self.data_loader.load_all_datasets()
        
        # 2. Extract texts
        logger.info("Phase 2: Extracting texts")
        all_texts = []
        for dataset_name, dataset in datasets.items():
            if dataset_name == 'wikitext':
                texts = dataset['train']['text'][:10000]
            elif dataset_name == 'news':
                texts = dataset['train']['text'][:10000]
            elif dataset_name == 'social_media':
                texts = dataset['text'][:10000]
            else:
                texts = []
            
            all_texts.extend(texts)
        
        logger.info(f"Extracted {len(all_texts)} texts")
        
        # 3. Analyze vocabulary
        logger.info("Phase 3: Analyzing vocabulary")
        vocab = self.analyzer.extract_vocabulary(all_texts)
        ngrams = self.analyzer.extract_ngrams(all_texts, n=2)
        
        # 4. Predict future
        logger.info("Phase 4: Predicting future language")
        future_predictions = self.predictor.extrapolate_trends({'emerging_words': list(vocab.items())[:100], 'declining_words': list(vocab.items())[-100:]})
        neologism_predictions = self.predictor.predict_neologisms(list(vocab.keys())[:50], [])
        language_features = self.predictor.predict_language_features()
        
        # 5. Test with ChatGPT
        logger.info("Phase 5: Testing with ChatGPT")
        test_texts = [
            "The future of artificial intelligence is",
            "In 20 years, people will communicate through",
            "Technology will change language by"
        ]
        
        chatgpt_predictions = {}
        for text in test_texts:
            next_words = self.chatgpt_predictor.predict_next_word(text)
            future_text = self.chatgpt_predictor.predict_future_language(text, years_ahead=20)
            chatgpt_predictions[text] = {
                'next_words': next_words,
                'future_prediction': future_text
            }
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'vocabulary_size': len(vocab),
            'ngrams_analyzed': len(ngrams),
            'future_predictions': future_predictions,
            'neologism_predictions': neologism_predictions,
            'language_features_2044': language_features,
            'chatgpt_predictions': chatgpt_predictions
        }
        
        logger.info("Analysis complete!")
        return results
    
    def save_results(self, results: Dict, output_file: str = "future_language_predictions.json"):
        """Save results to file"""
        logger.info(f"Saving results to {output_file}")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Results saved!")


if __name__ == "__main__":
    # Run the system
    system = FutureLanguagePredictionSystem()
    results = system.run_full_analysis()
    system.save_results(results)
    
    # Print summary
    print("\n" + "="*80)
    print("FUTURE LANGUAGE PREDICTION - SUMMARY")
    print("="*80)
    print(f"Vocabulary analyzed: {results['vocabulary_size']}")
    print(f"N-grams analyzed: {results['ngrams_analyzed']}")
    print(f"Target year: 2044")
    print("\nLanguage features in 2044:")
    for feature, value in results['language_features_2044'].items():
        print(f"  {feature}: {value}")
    print("="*80)
