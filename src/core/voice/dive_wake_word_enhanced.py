#!/usr/bin/env python3
"""
Dive AI V25.1 - Enhanced Wake Word Detection
Fixes transcription errors like "Hay Day" → "hey dive"
Supports phonetic matching and fuzzy recognition
"""

import re
from typing import List, Tuple, Optional
from difflib import SequenceMatcher


class EnhancedWakeWordDetector:
    """
    Enhanced wake word detection with phonetic matching
    Handles common transcription errors and accent variations
    """
    
    def __init__(self, wake_word: str = "hey dive", confidence_threshold: float = 0.7):
        self.wake_word = wake_word.lower()
        self.confidence_threshold = confidence_threshold
        
        # Phonetic variations and common transcription errors
        self.phonetic_variations = self._generate_phonetic_variations(wake_word)
        
        print(f"✓ Enhanced Wake Word Detector initialized")
        print(f"  Target: '{wake_word}'")
        print(f"  Variations: {len(self.phonetic_variations)} patterns")
    
    def _generate_phonetic_variations(self, wake_word: str) -> List[str]:
        """
        Generate phonetic variations of the wake word
        Handles common transcription errors
        """
        variations = [wake_word.lower()]
        
        # For "hey dive"
        if "hey dive" in wake_word.lower():
            variations.extend([
                "hay day",           # Common error
                "hey day",           # Partial error
                "hay dive",          # Partial error
                "hey dives",         # Plural error
                "hay dives",         # Combined error
                "a dive",            # Missing 'h'
                "hey die",           # 'v' → 'e'
                "hey dive",          # Correct
                "hei dive",          # 'y' → 'i'
                "hey dai",           # 'v' → 'i'
                "hey dibe",          # 'v' → 'b'
                "hey dyve",          # 'i' → 'y'
                "hey dife",          # 'v' → 'f'
                "a day",             # Severe error
                "hey dav",           # Missing 'e'
                "hey div",           # Missing 'e'
                "heyday",            # No space
                "hey dime",          # 'm' for 'v'
                "hey dive",          # Double space
                "hey  dive",         # Extra space
            ])
        
        # Remove duplicates
        variations = list(set(variations))
        
        return variations
    
    def detect(self, text: str) -> Tuple[bool, float, Optional[str]]:
        """
        Detect wake word in text with confidence score
        
        Returns:
            (detected: bool, confidence: float, matched_variant: str)
        """
        text_lower = text.lower().strip()
        
        # 1. Exact match
        if self.wake_word in text_lower:
            return (True, 1.0, self.wake_word)
        
        # 2. Check phonetic variations
        for variation in self.phonetic_variations:
            if variation in text_lower:
                confidence = self._calculate_confidence(variation, self.wake_word)
                if confidence >= self.confidence_threshold:
                    return (True, confidence, variation)
        
        # 3. Fuzzy matching (for close matches)
        best_match, best_confidence = self._fuzzy_match(text_lower)
        if best_confidence >= self.confidence_threshold:
            return (True, best_confidence, best_match)
        
        return (False, 0.0, None)
    
    def _calculate_confidence(self, detected: str, target: str) -> float:
        """Calculate confidence score between detected and target"""
        # Use sequence matcher for similarity
        similarity = SequenceMatcher(None, detected, target).ratio()
        
        # Boost confidence for known variations
        if detected in self.phonetic_variations:
            similarity = max(similarity, 0.85)
        
        return similarity
    
    def _fuzzy_match(self, text: str) -> Tuple[Optional[str], float]:
        """
        Fuzzy match against wake word
        Handles typos and slight variations
        """
        words = text.split()
        best_match = None
        best_confidence = 0.0
        
        # Check all 2-word combinations
        for i in range(len(words) - 1):
            phrase = f"{words[i]} {words[i+1]}"
            confidence = SequenceMatcher(None, phrase, self.wake_word).ratio()
            
            if confidence > best_confidence:
                best_confidence = confidence
                best_match = phrase
        
        # Check single words against wake word
        for word in words:
            confidence = SequenceMatcher(None, word, self.wake_word).ratio()
            if confidence > best_confidence:
                best_confidence = confidence
                best_match = word
        
        return (best_match, best_confidence)
    
    def extract_command(self, text: str, matched_variant: str) -> str:
        """
        Extract command after wake word
        
        Args:
            text: Full transcribed text
            matched_variant: The variant that was matched
        
        Returns:
            Command text without wake word
        """
        text_lower = text.lower()
        
        # Find position of matched variant
        if matched_variant in text_lower:
            # Remove wake word and everything before it
            parts = text_lower.split(matched_variant, 1)
            if len(parts) > 1:
                return parts[1].strip()
        
        # Fallback: return original text
        return text.strip()


class PhoneticTranscriptionFixer:
    """
    Fix common transcription errors in real-time
    Especially for Vietnamese-accented English
    """
    
    def __init__(self):
        # Common transcription error mappings
        self.error_mappings = {
            # Vietnamese accent errors
            "hay day": "hey dive",
            "hey day": "hey dive",
            "hay dive": "hey dive",
            "a day": "hey dive",
            "heyday": "hey dive",
            
            # Chrome variations
            "crom": "chrome",
            "krom": "chrome",
            "chrom": "chrome",
            "crone": "chrome",
            
            # Common words
            "opan": "open",
            "opin": "open",
            "clouse": "close",
            "closs": "close",
            "surch": "search",
            "serch": "search",
            "seach": "search",
            "navicat": "navigate",
            "navigat": "navigate",
        }
    
    def fix(self, text: str) -> str:
        """
        Fix common transcription errors
        
        Args:
            text: Transcribed text with potential errors
        
        Returns:
            Corrected text
        """
        text_lower = text.lower()
        corrected = text_lower
        
        # Apply error mappings
        for error, correction in self.error_mappings.items():
            if error in corrected:
                corrected = corrected.replace(error, correction)
                print(f"🔧 Fixed: '{error}' → '{correction}'")
        
        return corrected


class AccentAwareSTT:
    """
    Accent-aware Speech-to-Text wrapper
    Enhances recognition for Vietnamese-accented English
    """
    
    def __init__(self, base_recognizer, language: str = "en-US"):
        self.recognizer = base_recognizer
        self.language = language
        self.fixer = PhoneticTranscriptionFixer()
        
        # Custom vocabulary hints for better recognition
        self.vocabulary_hints = [
            "hey dive",
            "chrome",
            "open",
            "close",
            "search",
            "navigate",
            "github",
            "google",
        ]
    
    def recognize(self, audio, method: str = "google") -> Optional[str]:
        """
        Recognize speech with accent awareness
        
        Args:
            audio: Audio data
            method: Recognition method (google, whisper, sphinx)
        
        Returns:
            Transcribed and corrected text
        """
        try:
            # Perform recognition
            if method == "google":
                text = self.recognizer.recognize_google(
                    audio,
                    language=self.language,
                    show_all=False
                )
            elif method == "whisper":
                # Whisper with custom vocabulary
                text = self.recognizer.recognize_whisper(
                    audio,
                    language=self.language.split("-")[0]
                )
            else:
                text = self.recognizer.recognize_sphinx(audio)
            
            # Apply transcription fixes
            if text:
                corrected = self.fixer.fix(text)
                if corrected != text.lower():
                    print(f"📝 Original: {text}")
                    print(f"📝 Corrected: {corrected}")
                return corrected
            
            return text
        
        except Exception as e:
            print(f"⚠ Recognition error: {e}")
            return None


# Example usage and testing
if __name__ == "__main__":
    # Test wake word detection
    detector = EnhancedWakeWordDetector("hey dive", confidence_threshold=0.7)
    
    test_phrases = [
        "hey dive open chrome",
        "hay day open chrome",
        "hey day search for something",
        "a day close window",
        "heyday navigate to github",
        "hey dives what's the weather",
        "random text without wake word",
        "hey dive",
        "hay day",
    ]
    
    print("\n" + "="*70)
    print("WAKE WORD DETECTION TESTS")
    print("="*70)
    
    for phrase in test_phrases:
        detected, confidence, matched = detector.detect(phrase)
        status = "✓" if detected else "✗"
        print(f"\n{status} Input: '{phrase}'")
        print(f"  Detected: {detected}")
        print(f"  Confidence: {confidence:.2f}")
        print(f"  Matched: '{matched}'")
        
        if detected:
            command = detector.extract_command(phrase, matched)
            print(f"  Command: '{command}'")
    
    # Test transcription fixer
    print("\n" + "="*70)
    print("TRANSCRIPTION FIXER TESTS")
    print("="*70)
    
    fixer = PhoneticTranscriptionFixer()
    
    test_transcriptions = [
        "hay day opan crom",
        "hey day surch for github",
        "a day clouse window",
    ]
    
    for transcription in test_transcriptions:
        fixed = fixer.fix(transcription)
        print(f"\nOriginal: '{transcription}'")
        print(f"Fixed:    '{fixed}'")
