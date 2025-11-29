#!/usr/bin/env python3
"""
Test script to verify AI assessment evaluation is working
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.assessment_service import AssessmentScoringService


async def test_ai_evaluation():
    """Test AI evaluation with various answers"""
    
    print("=" * 60)
    print("Testing AI Assessment Evaluation")
    print("=" * 60)
    
    service = AssessmentScoringService()
    
    # Test cases
    test_cases = [
        {
            "question": "What year is it?",
            "user_answer": "2024",
            "expected": "2024",
            "context": "MMSE Orientation to Time",
            "should_pass": True
        },
        {
            "question": "What year is it?",
            "user_answer": "twenty twenty four",
            "expected": "2024",
            "context": "MMSE Orientation to Time",
            "should_pass": True
        },
        {
            "question": "What season is it?",
            "user_answer": "autumn",
            "expected": "fall",
            "context": "MMSE Orientation to Time",
            "should_pass": True
        },
        {
            "question": "What season is it?",
            "user_answer": "fall",
            "expected": "fall",
            "context": "MMSE Orientation to Time",
            "should_pass": True
        },
        {
            "question": "What season is it?",
            "user_answer": "spring",
            "expected": "fall",
            "context": "MMSE Orientation to Time",
            "should_pass": False
        },
        {
            "question": "Repeat these words: APPLE, TABLE, PENNY",
            "user_answer": "apple table penny",
            "expected": "apple, table, penny",
            "context": "MMSE Registration",
            "should_pass": True
        },
        {
            "question": "Repeat these words: APPLE, TABLE, PENNY",
            "user_answer": "apple, table, and penny",
            "expected": "apple, table, penny",
            "context": "MMSE Registration",
            "should_pass": True
        },
        {
            "question": "What do you call this writing instrument?",
            "user_answer": "pen",
            "expected": "pencil",
            "context": "MMSE Naming",
            "should_pass": True  # Both pen and pencil are acceptable
        },
        {
            "question": "Write a complete sentence",
            "user_answer": "The sun is shining today.",
            "expected": "any complete sentence",
            "context": "MMSE Writing",
            "should_pass": True
        },
        {
            "question": "Write a complete sentence",
            "user_answer": "running fast",
            "expected": "any complete sentence",
            "context": "MMSE Writing",
            "should_pass": False
        }
    ]
    
    passed = 0
    failed = 0
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'─' * 60}")
        print(f"Test {i}/{len(test_cases)}")
        print(f"Question: {test['question']}")
        print(f"User Answer: '{test['user_answer']}'")
        print(f"Expected: '{test['expected']}'")
        print(f"Should Pass: {test['should_pass']}")
        
        try:
            result = await service.evaluate_answer(
                question=test['question'],
                user_answer=test['user_answer'],
                expected_answer=test['expected'],
                context=test['context']
            )
            
            print(f"AI Result: {'✅ CORRECT' if result else '❌ INCORRECT'}")
            
            if result == test['should_pass']:
                print(f"Status: ✅ PASS")
                passed += 1
            else:
                print(f"Status: ❌ FAIL (Expected {test['should_pass']}, got {result})")
                failed += 1
                
        except Exception as e:
            print(f"Status: ❌ ERROR - {str(e)}")
            failed += 1
    
    print(f"\n{'=' * 60}")
    print(f"Results: {passed} passed, {failed} failed out of {len(test_cases)} tests")
    print(f"Success Rate: {(passed/len(test_cases)*100):.1f}%")
    print(f"{'=' * 60}")
    
    return passed, failed


async def test_gemini_availability():
    """Test if Gemini service is available"""
    print("\n" + "=" * 60)
    print("Testing Gemini Service Availability")
    print("=" * 60)
    
    service = AssessmentScoringService()
    
    if service.gemini_service.is_available():
        print("✅ Gemini service is configured and available")
        print(f"   Model: {service.gemini_service.model_name}")
        print(f"   API Key: {service.gemini_service.api_key[:20]}...")
        return True
    else:
        print("❌ Gemini service is NOT available")
        print("   Check GEMINI_API_KEY in backend/.env")
        return False


async def main():
    """Run all tests"""
    print("\n🧪 AI Assessment Evaluation Test Suite\n")
    
    # Test 1: Check Gemini availability
    gemini_available = await test_gemini_availability()
    
    if not gemini_available:
        print("\n⚠️  Cannot proceed with tests - Gemini not available")
        return
    
    # Test 2: Run evaluation tests
    passed, failed = await test_ai_evaluation()
    
    # Summary
    print("\n" + "=" * 60)
    if failed == 0:
        print("🎉 All tests passed! AI evaluation is working correctly.")
    else:
        print(f"⚠️  {failed} test(s) failed. Review the results above.")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
