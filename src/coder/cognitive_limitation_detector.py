#!/usr/bin/env python3
"""
Cognitive Limitation Detector
Identifies restricted thinking patterns, biases, and mental model limitations
"""

import openai
import re
from typing import Dict, List, Tuple, Optional
import logging
from collections import Counter, defaultdict
from dataclasses import dataclass
import json
from datetime import datetime
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

openai.api_key = os.environ.get("OPENAI_API_KEY")


# ========== DATA STRUCTURES ==========

@dataclass
class CognitiveBias:
    """Detected cognitive bias"""
    bias_name: str
    bias_type: str  # confirmation, anchoring, availability, etc.
    description: str
    evidence: str
    severity: float  # 0-1
    impact: str


@dataclass
class MentalModel:
    """Identified mental model"""
    model_name: str
    assumptions: List[str]
    limitations: List[str]
    scope: str
    flexibility: float  # 0-1 (how rigid)


@dataclass
class ThinkingPattern:
    """Identified thinking pattern"""
    pattern_name: str
    pattern_type: str  # linear, binary, fixed, etc.
    description: str
    occurrences: int
    examples: List[str]
    restriction_level: float  # 0-1


@dataclass
class PerspectiveLimitation:
    """Identified perspective limitation"""
    limitation_name: str
    current_perspective: str
    alternative_perspectives: List[str]
    blind_spots: List[str]
    expansion_suggestions: List[str]


@dataclass
class CognitiveAnalysisResult:
    """Complete cognitive analysis"""
    input_text: str
    biases_detected: List[CognitiveBias]
    mental_models: List[MentalModel]
    thinking_patterns: List[ThinkingPattern]
    perspective_limitations: List[PerspectiveLimitation]
    overall_restriction_score: float  # 0-1
    expansion_recommendations: List[str]
    timestamp: str


# ========== COGNITIVE BIAS DETECTOR ==========

class CognitiveBiasDetector:
    """Detect cognitive biases in thinking"""
    
    def __init__(self):
        self.bias_patterns = self._build_bias_patterns()
        logger.info("Initialized Cognitive Bias Detector")
    
    def _build_bias_patterns(self) -> Dict[str, Dict]:
        """Build patterns for detecting biases"""
        return {
            'confirmation_bias': {
                'keywords': ['always', 'never', 'obviously', 'clearly', 'everyone knows', 'of course'],
                'patterns': [r'only.*because', r'.*proves.*', r'.*obviously.*'],
                'description': 'Seeking only information that confirms existing beliefs'
            },
            'anchoring_bias': {
                'keywords': ['first', 'initial', 'starting point', 'baseline', 'reference'],
                'patterns': [r'start.*with', r'based.*on.*first', r'anchor.*to'],
                'description': 'Over-relying on first piece of information'
            },
            'availability_bias': {
                'keywords': ['recent', 'memorable', 'famous', 'popular', 'trending'],
                'patterns': [r'.*recently.*', r'.*everyone.*', r'.*common.*'],
                'description': 'Judging probability by how easily examples come to mind'
            },
            'sunk_cost_fallacy': {
                'keywords': ['invested', 'already spent', 'can\'t waste', 'too much effort'],
                'patterns': [r'.*invested.*', r'.*already.*spent.*', r'.*can\'t.*waste.*'],
                'description': 'Continuing because of past investment rather than future value'
            },
            'hindsight_bias': {
                'keywords': ['obvious', 'predictable', 'should have known', 'always knew'],
                'patterns': [r'.*obvious.*', r'.*should.*have.*', r'.*always.*knew.*'],
                'description': 'Believing past events were more predictable than they were'
            },
            'dunning_kruger': {
                'keywords': ['simple', 'easy', 'anyone can', 'no problem', 'straightforward'],
                'patterns': [r'.*simple.*', r'.*easy.*', r'.*anyone.*can.*'],
                'description': 'Overestimating competence in areas of limited knowledge'
            },
            'groupthink': {
                'keywords': ['everyone', 'we all', 'obviously', 'common sense', 'normal'],
                'patterns': [r'.*everyone.*', r'.*we.*all.*', r'.*common.*sense.*'],
                'description': 'Conforming to group opinion without critical analysis'
            },
            'black_white_thinking': {
                'keywords': ['always', 'never', 'all', 'none', 'completely', 'totally'],
                'patterns': [r'.*always.*', r'.*never.*', r'.*all.*or.*none.*'],
                'description': 'Seeing situations in only two extremes'
            },
            'fundamental_attribution_error': {
                'keywords': ['personality', 'character', 'nature', 'type of person', 'just is'],
                'patterns': [r'.*is.*type.*', r'.*character.*', r'.*just.*is.*'],
                'description': 'Attributing others\' behavior to personality rather than situation'
            },
            'status_quo_bias': {
                'keywords': ['always been', 'tradition', 'how it works', 'normal', 'standard'],
                'patterns': [r'.*always.*been.*', r'.*tradition.*', r'.*how.*it.*works.*'],
                'description': 'Preferring current state without considering alternatives'
            }
        }
    
    def detect_biases(self, text: str) -> List[CognitiveBias]:
        """Detect biases in text"""
        detected_biases = []
        text_lower = text.lower()
        
        for bias_name, bias_info in self.bias_patterns.items():
            severity = 0
            evidence = ""
            
            # Check keywords
            for keyword in bias_info['keywords']:
                if keyword in text_lower:
                    severity += 0.1
                    evidence += f"Found keyword: '{keyword}'. "
            
            # Check patterns
            for pattern in bias_info['patterns']:
                if re.search(pattern, text_lower):
                    severity += 0.15
                    evidence += f"Found pattern: {pattern}. "
            
            if severity > 0:
                detected_biases.append(CognitiveBias(
                    bias_name=bias_name.replace('_', ' ').title(),
                    bias_type=bias_name,
                    description=bias_info['description'],
                    evidence=evidence.strip(),
                    severity=min(severity, 1.0),
                    impact=self._assess_impact(bias_name, severity)
                ))
        
        return sorted(detected_biases, key=lambda x: x.severity, reverse=True)
    
    def _assess_impact(self, bias_type: str, severity: float) -> str:
        """Assess impact of bias"""
        if severity > 0.7:
            return "HIGH - Significantly restricts thinking"
        elif severity > 0.4:
            return "MEDIUM - Moderately restricts thinking"
        else:
            return "LOW - Slightly restricts thinking"


# ========== MENTAL MODEL ANALYZER ==========

class MentalModelAnalyzer:
    """Analyze mental models and their limitations"""
    
    def __init__(self):
        self.common_models = self._build_common_models()
        logger.info("Initialized Mental Model Analyzer")
    
    def _build_common_models(self) -> Dict[str, Dict]:
        """Build common mental models"""
        return {
            'linear_thinking': {
                'assumptions': [
                    'Cause leads directly to effect',
                    'More input = more output',
                    'Progress is steady and predictable',
                    'Problems have single solutions'
                ],
                'limitations': [
                    'Misses feedback loops',
                    'Ignores non-linear dynamics',
                    'Fails with complex systems',
                    'Overlooks tipping points'
                ],
                'scope': 'Simple, isolated systems'
            },
            'binary_thinking': {
                'assumptions': [
                    'Things are either good or bad',
                    'Success or failure, nothing between',
                    'Right or wrong, no gray area',
                    'Us vs them mentality'
                ],
                'limitations': [
                    'Misses nuance and complexity',
                    'Creates false dichotomies',
                    'Ignores spectrum of possibilities',
                    'Oversimplifies reality'
                ],
                'scope': 'Moral and categorical judgments'
            },
            'fixed_mindset': {
                'assumptions': [
                    'Abilities are fixed and unchangeable',
                    'Effort is for people without talent',
                    'Challenges are threats',
                    'Failure is permanent'
                ],
                'limitations': [
                    'Avoids growth opportunities',
                    'Gives up too easily',
                    'Sees effort as weakness',
                    'Limits potential'
                ],
                'scope': 'Personal development and learning'
            },
            'scarcity_mindset': {
                'assumptions': [
                    'Resources are limited',
                    'Someone else\'s gain is my loss',
                    'Competition is zero-sum',
                    'Must hoard and protect'
                ],
                'limitations': [
                    'Misses collaboration opportunities',
                    'Creates unnecessary conflict',
                    'Ignores abundance possibilities',
                    'Prevents sharing and growth'
                ],
                'scope': 'Resource allocation and relationships'
            },
            'mechanistic_thinking': {
                'assumptions': [
                    'Systems work like machines',
                    'Predictable and controllable',
                    'Parts are independent',
                    'Can be fully understood'
                ],
                'limitations': [
                    'Fails with organic systems',
                    'Misses emergence and complexity',
                    'Ignores adaptive behavior',
                    'Overlooks unintended consequences'
                ],
                'scope': 'Complex adaptive systems'
            },
            'either_or_thinking': {
                'assumptions': [
                    'Must choose between options',
                    'Can\'t have both',
                    'Tradeoffs are inevitable',
                    'One is always better'
                ],
                'limitations': [
                    'Misses third options',
                    'Ignores creative solutions',
                    'Accepts false constraints',
                    'Limits innovation'
                ],
                'scope': 'Decision-making and problem-solving'
            }
        }
    
    def analyze_mental_models(self, text: str) -> List[MentalModel]:
        """Analyze mental models in text"""
        detected_models = []
        text_lower = text.lower()
        
        for model_name, model_info in self.common_models.items():
            # Check for model indicators
            indicators = model_info['assumptions'] + model_info['limitations']
            match_count = sum(1 for indicator in indicators if indicator.lower() in text_lower)
            
            if match_count > 0:
                flexibility = 1.0 - (match_count / len(indicators))
                
                detected_models.append(MentalModel(
                    model_name=model_name.replace('_', ' ').title(),
                    assumptions=model_info['assumptions'],
                    limitations=model_info['limitations'],
                    scope=model_info['scope'],
                    flexibility=flexibility
                ))
        
        return sorted(detected_models, key=lambda x: x.flexibility)


# ========== THINKING PATTERN RECOGNIZER ==========

class ThinkingPatternRecognizer:
    """Recognize restricted thinking patterns"""
    
    def __init__(self):
        self.patterns = self._build_patterns()
        logger.info("Initialized Thinking Pattern Recognizer")
    
    def _build_patterns(self) -> Dict[str, Dict]:
        """Build thinking patterns"""
        return {
            'linear_progression': {
                'description': 'Assumes linear progression without considering cycles or jumps',
                'indicators': ['then', 'next', 'after', 'following', 'step by step'],
                'restriction': 0.6
            },
            'single_causality': {
                'description': 'Attributes effects to single causes',
                'indicators': ['because', 'caused by', 'due to', 'reason is', 'caused'],
                'restriction': 0.7
            },
            'extrapolation': {
                'description': 'Extends current trends indefinitely into future',
                'indicators': ['always', 'never', 'forever', 'will continue', 'trend'],
                'restriction': 0.8
            },
            'categorical_thinking': {
                'description': 'Places things into fixed categories',
                'indicators': ['type of', 'kind of', 'category', 'class of', 'group'],
                'restriction': 0.5
            },
            'deterministic_thinking': {
                'description': 'Believes outcomes are predetermined',
                'indicators': ['must', 'have to', 'inevitable', 'certain', 'will definitely'],
                'restriction': 0.75
            },
            'either_or_logic': {
                'description': 'Sees only two options without middle ground',
                'indicators': ['either', 'or', 'both', 'neither', 'choose between'],
                'restriction': 0.8
            },
            'past_focused': {
                'description': 'Heavily relies on past without considering new possibilities',
                'indicators': ['always been', 'historically', 'traditionally', 'in the past'],
                'restriction': 0.7
            },
            'present_focused': {
                'description': 'Focuses only on immediate present',
                'indicators': ['now', 'today', 'currently', 'at this moment', 'right now'],
                'restriction': 0.6
            }
        }
    
    def recognize_patterns(self, text: str) -> List[ThinkingPattern]:
        """Recognize thinking patterns"""
        patterns = []
        text_lower = text.lower()
        
        for pattern_name, pattern_info in self.patterns.items():
            occurrences = 0
            examples = []
            
            for indicator in pattern_info['indicators']:
                count = text_lower.count(indicator)
                occurrences += count
                if count > 0:
                    examples.append(f"'{indicator}' (x{count})")
            
            if occurrences > 0:
                patterns.append(ThinkingPattern(
                    pattern_name=pattern_name.replace('_', ' ').title(),
                    pattern_type=pattern_name,
                    description=pattern_info['description'],
                    occurrences=occurrences,
                    examples=examples,
                    restriction_level=pattern_info['restriction']
                ))
        
        return sorted(patterns, key=lambda x: x.occurrences, reverse=True)


# ========== PERSPECTIVE LIMITATION DETECTOR ==========

class PerspectiveLimitationDetector:
    """Detect perspective limitations"""
    
    def __init__(self):
        self.perspectives = self._build_perspectives()
        logger.info("Initialized Perspective Limitation Detector")
    
    def _build_perspectives(self) -> Dict[str, Dict]:
        """Build alternative perspectives"""
        return {
            'individual_perspective': {
                'current': 'Individual/personal viewpoint',
                'alternatives': [
                    'Systems perspective - how parts interact',
                    'Community perspective - collective impact',
                    'Global perspective - worldwide implications',
                    'Historical perspective - long-term patterns',
                    'Future perspective - long-term consequences'
                ],
                'blind_spots': [
                    'Misses systemic issues',
                    'Ignores collective effects',
                    'Overlooks historical context',
                    'Doesn\'t consider future impact'
                ]
            },
            'short_term_perspective': {
                'current': 'Short-term/immediate focus',
                'alternatives': [
                    'Long-term perspective - future consequences',
                    'Generational perspective - multi-generational impact',
                    'Historical perspective - historical patterns',
                    'Evolutionary perspective - adaptation over time',
                    'Cyclical perspective - recurring patterns'
                ],
                'blind_spots': [
                    'Misses long-term consequences',
                    'Ignores compound effects',
                    'Overlooks historical patterns',
                    'Fails to anticipate future'
                ]
            },
            'western_perspective': {
                'current': 'Western/individualistic worldview',
                'alternatives': [
                    'Eastern/collectivist perspective',
                    'Indigenous perspective - nature connection',
                    'Non-Western philosophical traditions',
                    'Diverse cultural frameworks',
                    'Holistic worldviews'
                ],
                'blind_spots': [
                    'Misses collectivist values',
                    'Ignores non-Western wisdom',
                    'Overlooks nature connection',
                    'Fails to appreciate diversity'
                ]
            },
            'rational_perspective': {
                'current': 'Purely rational/logical thinking',
                'alternatives': [
                    'Emotional perspective - feelings and intuition',
                    'Spiritual perspective - meaning and purpose',
                    'Aesthetic perspective - beauty and form',
                    'Embodied perspective - physical experience',
                    'Intuitive perspective - gut feelings'
                ],
                'blind_spots': [
                    'Misses emotional dimensions',
                    'Ignores intuitive wisdom',
                    'Overlooks spiritual meaning',
                    'Fails to value non-rational ways of knowing'
                ]
            },
            'expert_perspective': {
                'current': 'Expert/specialist viewpoint',
                'alternatives': [
                    'Generalist perspective - broad connections',
                    'Beginner perspective - fresh questions',
                    'Outsider perspective - external view',
                    'Interdisciplinary perspective - cross-domain insights',
                    'Naive perspective - questioning assumptions'
                ],
                'blind_spots': [
                    'Misses broader connections',
                    'Overlooks basic questions',
                    'Fails to see from outside',
                    'Gets trapped in domain thinking'
                ]
            }
        }
    
    def detect_limitations(self, text: str) -> List[PerspectiveLimitation]:
        """Detect perspective limitations"""
        limitations = []
        text_lower = text.lower()
        
        # Simple heuristics to detect perspective
        detected_perspectives = []
        
        if any(word in text_lower for word in ['i', 'me', 'my', 'personal', 'individual']):
            detected_perspectives.append('individual_perspective')
        
        if any(word in text_lower for word in ['now', 'today', 'immediate', 'quick', 'fast']):
            detected_perspectives.append('short_term_perspective')
        
        if any(word in text_lower for word in ['logic', 'rational', 'reason', 'fact', 'data']):
            detected_perspectives.append('rational_perspective')
        
        if any(word in text_lower for word in ['expert', 'specialist', 'professional', 'field']):
            detected_perspectives.append('expert_perspective')
        
        for perspective in detected_perspectives:
            if perspective in self.perspectives:
                persp_info = self.perspectives[perspective]
                limitations.append(PerspectiveLimitation(
                    limitation_name=perspective.replace('_', ' ').title(),
                    current_perspective=persp_info['current'],
                    alternative_perspectives=persp_info['alternatives'],
                    blind_spots=persp_info['blind_spots'],
                    expansion_suggestions=[
                        f"Consider: {alt}" for alt in persp_info['alternatives']
                    ]
                ))
        
        return limitations


# ========== COGNITIVE LIMITATION ANALYZER ==========

class CognitiveLimitationAnalyzer:
    """Main analyzer combining all detectors"""
    
    def __init__(self):
        self.bias_detector = CognitiveBiasDetector()
        self.model_analyzer = MentalModelAnalyzer()
        self.pattern_recognizer = ThinkingPatternRecognizer()
        self.perspective_detector = PerspectiveLimitationDetector()
        
        logger.info("Initialized Cognitive Limitation Analyzer")
    
    def analyze(self, text: str) -> CognitiveAnalysisResult:
        """Complete cognitive analysis"""
        
        logger.info(f"Analyzing text: {text[:100]}...")
        
        # Detect all limitations
        biases = self.bias_detector.detect_biases(text)
        models = self.model_analyzer.analyze_mental_models(text)
        patterns = self.pattern_recognizer.recognize_patterns(text)
        perspectives = self.perspective_detector.detect_limitations(text)
        
        # Calculate overall restriction score
        bias_score = sum(b.severity for b in biases) / len(biases) if biases else 0
        model_score = sum(1 - m.flexibility for m in models) / len(models) if models else 0
        pattern_score = sum(p.restriction_level for p in patterns) / len(patterns) if patterns else 0
        
        overall_score = (bias_score + model_score + pattern_score) / 3
        
        # Generate recommendations
        recommendations = self._generate_recommendations(biases, models, patterns, perspectives)
        
        return CognitiveAnalysisResult(
            input_text=text,
            biases_detected=biases,
            mental_models=models,
            thinking_patterns=patterns,
            perspective_limitations=perspectives,
            overall_restriction_score=overall_score,
            expansion_recommendations=recommendations,
            timestamp=datetime.now().isoformat()
        )
    
    def _generate_recommendations(self, biases, models, patterns, perspectives) -> List[str]:
        """Generate expansion recommendations"""
        recommendations = []
        
        # Bias-based recommendations
        if biases:
            top_bias = biases[0]
            recommendations.append(f"Address {top_bias.bias_name}: Actively seek disconfirming evidence")
        
        # Model-based recommendations
        if models:
            most_rigid = min(models, key=lambda x: x.flexibility)
            recommendations.append(f"Challenge {most_rigid.model_name}: Consider non-linear dynamics and complex systems")
        
        # Pattern-based recommendations
        if patterns:
            top_pattern = patterns[0]
            recommendations.append(f"Break {top_pattern.pattern_name}: Explore non-linear progressions and multiple causalities")
        
        # Perspective-based recommendations
        if perspectives:
            recommendations.extend([
                f"Adopt {p.limitation_name}: {p.alternative_perspectives[0]}" 
                for p in perspectives[:2]
            ])
        
        return recommendations


# ========== MAIN ==========

def main():
    """Example usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Cognitive Limitation Detector")
    parser.add_argument("--text", default="This will never work because we've always done it this way. Everyone knows that success requires talent, not effort. Obviously, this is the right approach.", help="Text to analyze")
    
    args = parser.parse_args()
    
    # Initialize analyzer
    analyzer = CognitiveLimitationAnalyzer()
    
    # Analyze
    logger.info(f"Input: '{args.text}'")
    result = analyzer.analyze(args.text)
    
    # Print results
    print("\n" + "="*80)
    print("COGNITIVE LIMITATION ANALYSIS")
    print("="*80)
    print(f"\nInput: {result.input_text}\n")
    
    print(f"Overall Restriction Score: {result.overall_restriction_score:.1%}")
    print("(Higher = more restricted thinking)\n")
    
    if result.biases_detected:
        print("COGNITIVE BIASES DETECTED:")
        for bias in result.biases_detected:
            print(f"  • {bias.bias_name} ({bias.bias_type})")
            print(f"    Severity: {bias.severity:.1%}")
            print(f"    Impact: {bias.impact}")
            print(f"    Evidence: {bias.evidence}\n")
    
    if result.mental_models:
        print("\nMENTAL MODELS IDENTIFIED:")
        for model in result.mental_models:
            print(f"  • {model.model_name}")
            print(f"    Flexibility: {model.flexibility:.1%}")
            print(f"    Scope: {model.scope}\n")
    
    if result.thinking_patterns:
        print("\nTHINKING PATTERNS:")
        for pattern in result.thinking_patterns:
            print(f"  • {pattern.pattern_name}")
            print(f"    Restriction Level: {pattern.restriction_level:.1%}")
            print(f"    Occurrences: {pattern.occurrences}\n")
    
    if result.perspective_limitations:
        print("\nPERSPECTIVE LIMITATIONS:")
        for persp in result.perspective_limitations:
            print(f"  • {persp.limitation_name}")
            print(f"    Current: {persp.current_perspective}")
            print(f"    Blind Spots: {', '.join(persp.blind_spots[:2])}\n")
    
    print("\nEXPANSION RECOMMENDATIONS:")
    for i, rec in enumerate(result.expansion_recommendations, 1):
        print(f"  {i}. {rec}")
    
    print("\n" + "="*80)


if __name__ == "__main__":
    main()
