#!/usr/bin/env python3
"""
Dive AI V25.3 - Test Suite
Tests for multimodal voice + vision features
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

def test_wake_word_detection():
    """Test enhanced wake word detection"""
    print("\n" + "="*70)
    print("TEST 1: Wake Word Detection")
    print("="*70)
    
    try:
        from core.dive_wake_word_enhanced import EnhancedWakeWordDetector
        
        detector = EnhancedWakeWordDetector("hey dive", confidence_threshold=0.7)
        
        test_cases = [
            ("hey dive open chrome", True),
            ("hay day open chrome", True),  # Should be fixed
            ("hey day search for something", True),  # Should be fixed
            ("random text without wake word", False),
            ("heyday navigate to github", True),  # Should be fixed
        ]
        
        passed = 0
        failed = 0
        
        for text, expected in test_cases:
            detected, confidence, matched = detector.detect(text)
            status = "✓" if detected == expected else "✗"
            
            if detected == expected:
                passed += 1
            else:
                failed += 1
            
            print(f"\n{status} Input: '{text}'")
            print(f"  Expected: {expected}, Got: {detected}")
            print(f"  Confidence: {confidence:.2f}")
            if matched:
                print(f"  Matched: '{matched}'")
        
        print(f"\nResults: {passed} passed, {failed} failed")
        return failed == 0
    
    except Exception as e:
        print(f"⚠ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_transcription_fixer():
    """Test phonetic transcription fixer"""
    print("\n" + "="*70)
    print("TEST 2: Transcription Fixer")
    print("="*70)
    
    try:
        from core.dive_wake_word_enhanced import PhoneticTranscriptionFixer
        
        fixer = PhoneticTranscriptionFixer()
        
        test_cases = [
            ("hay day open crom", "hey dive open chrome"),
            ("hey day surch for github", "hey dive search for github"),
            ("a day clouse window", "hey dive close window"),
        ]
        
        passed = 0
        failed = 0
        
        for input_text, expected in test_cases:
            fixed = fixer.fix(input_text)
            status = "✓" if fixed == expected else "✗"
            
            if fixed == expected:
                passed += 1
            else:
                failed += 1
            
            print(f"\n{status} Input: '{input_text}'")
            print(f"  Expected: '{expected}'")
            print(f"  Got:      '{fixed}'")
        
        print(f"\nResults: {passed} passed, {failed} failed")
        return failed == 0
    
    except Exception as e:
        print(f"⚠ Test failed: {e}")
        return False


def test_vision_processor():
    """Test vision processor (basic functionality)"""
    print("\n" + "="*70)
    print("TEST 3: Vision Processor")
    print("="*70)
    
    try:
        from core.dive_vision import DiveVisionProcessor
        
        vision = DiveVisionProcessor()
        
        # Test screenshot capture
        print("\n[3.1] Testing screenshot capture...")
        image = vision.capture_screen()
        
        if image:
            print(f"✓ Screenshot captured: {image.width}x{image.height}")
        else:
            print("✗ Screenshot capture failed")
            return False
        
        # Test image encoding
        print("\n[3.2] Testing image encoding...")
        encoded = vision.encode_image(image)
        
        if encoded and len(encoded) > 0:
            print(f"✓ Image encoded: {len(encoded)} bytes")
        else:
            print("✗ Image encoding failed")
            return False
        
        # Test cache
        print("\n[3.3] Testing screenshot cache...")
        cached = vision.get_cached_screenshot(max_age=5.0)
        
        if cached:
            print(f"✓ Cached screenshot retrieved")
        else:
            print("✗ Cache retrieval failed")
            return False
        
        print("\n✓ All vision tests passed")
        return True
    
    except Exception as e:
        print(f"⚠ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_multimodal_config():
    """Test multimodal configuration"""
    print("\n" + "="*70)
    print("TEST 4: Multimodal Configuration")
    print("="*70)
    
    try:
        from core.dive_multimodal_orchestrator import MultimodalConfig
        
        # Test default config
        print("\n[4.1] Testing default configuration...")
        config = MultimodalConfig()
        
        assert config.voice_enabled == True
        assert config.vision_enabled == True
        assert config.wake_word == "hey dive"
        print("✓ Default configuration valid")
        
        # Test custom config
        print("\n[4.2] Testing custom configuration...")
        config = MultimodalConfig(
            voice_model="gpt-4o-realtime-preview",
            vision_model="gpt-4-vision-preview",
            wake_word="computer",
            session_timeout=60
        )
        
        assert config.voice_model == "gpt-4o-realtime-preview"
        assert config.vision_model == "gpt-4-vision-preview"
        assert config.wake_word == "computer"
        assert config.session_timeout == 60
        print("✓ Custom configuration valid")
        
        print("\n✓ All configuration tests passed")
        return True
    
    except Exception as e:
        print(f"⚠ Test failed: {e}")
        return False


def test_imports():
    """Test that all modules can be imported"""
    print("\n" + "="*70)
    print("TEST 5: Module Imports")
    print("="*70)
    
    modules = [
        "core.dive_realtime_voice",
        "core.dive_vision",
        "core.dive_wake_word_enhanced",
        "core.dive_multimodal_orchestrator",
    ]
    
    passed = 0
    failed = 0
    
    for module in modules:
        try:
            __import__(module)
            print(f"✓ {module}")
            passed += 1
        except ImportError as e:
            print(f"✗ {module}: {e}")
            failed += 1
    
    print(f"\nResults: {passed} passed, {failed} failed")
    return failed == 0


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*70)
    print("DIVE AI V25.3 - TEST SUITE")
    print("="*70)
    
    results = []
    
    # Run tests
    results.append(("Module Imports", test_imports()))
    results.append(("Wake Word Detection", test_wake_word_detection()))
    results.append(("Transcription Fixer", test_transcription_fixer()))
    results.append(("Vision Processor", test_vision_processor()))
    results.append(("Multimodal Config", test_multimodal_config()))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    failed = sum(1 for _, result in results if not result)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("\n🎉 All tests passed!")
        return True
    else:
        print(f"\n⚠ {failed} test(s) failed")
        return False


if __name__ == "__main__":
    import sys
    success = run_all_tests()
    sys.exit(0 if success else 1)
