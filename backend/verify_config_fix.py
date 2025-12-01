#!/usr/bin/env python3
"""
Verification script for CORS_ORIGINS fix
Run this to ensure the configuration changes work correctly
"""

import os
import sys

def test_cors_parsing():
    """Test CORS_ORIGINS parsing with various formats"""
    
    test_cases = [
        {
            'name': 'Empty string (Render default)',
            'value': '',
            'expected': ['http://localhost:3000']
        },
        {
            'name': 'Single URL',
            'value': 'https://example.com',
            'expected': ['https://example.com']
        },
        {
            'name': 'Multiple URLs (comma-separated)',
            'value': 'https://example.com,https://app.example.com',
            'expected': ['https://example.com', 'https://app.example.com']
        },
        {
            'name': 'Multiple URLs with spaces',
            'value': 'https://example.com , https://app.example.com',
            'expected': ['https://example.com', 'https://app.example.com']
        },
    ]
    
    print('=' * 60)
    print('CORS_ORIGINS Configuration Fix Verification')
    print('=' * 60)
    print()
    
    all_passed = True
    
    for test in test_cases:
        os.environ['CORS_ORIGINS'] = test['value']
        os.environ['ENVIRONMENT'] = 'development'
        
        # Clear cache to force reload
        from app.core.config import get_settings
        get_settings.cache_clear()
        
        try:
            settings = get_settings()
            result = settings.CORS_ORIGINS
            
            if result == test['expected']:
                print(f"✅ PASS: {test['name']}")
                print(f"   Input:    {test['value']!r}")
                print(f"   Output:   {result}")
            else:
                print(f"❌ FAIL: {test['name']}")
                print(f"   Input:    {test['value']!r}")
                print(f"   Expected: {test['expected']}")
                print(f"   Got:      {result}")
                all_passed = False
        except Exception as e:
            print(f"❌ ERROR: {test['name']}")
            print(f"   Input:    {test['value']!r}")
            print(f"   Error:    {e}")
            all_passed = False
        
        print()
    
    print('=' * 60)
    if all_passed:
        print('✅ All tests passed! Configuration fix is working correctly.')
        print()
        print('Next steps:')
        print('1. Commit and push changes to GitHub')
        print('2. Update CORS_ORIGINS in Render dashboard')
        print('3. Verify deployment succeeds')
        return 0
    else:
        print('❌ Some tests failed. Please review the configuration.')
        return 1

def test_app_import():
    """Test that the main app can be imported"""
    print('Testing FastAPI app import...')
    
    os.environ['ENVIRONMENT'] = 'development'
    os.environ['CORS_ORIGINS'] = ''
    
    try:
        from app.main import app
        print(f'✅ FastAPI app imported successfully')
        print(f'   App title: {app.title}')
        print()
        return True
    except Exception as e:
        print(f'❌ Failed to import FastAPI app')
        print(f'   Error: {e}')
        print()
        return False

if __name__ == '__main__':
    print()
    
    # Test app import first
    if not test_app_import():
        sys.exit(1)
    
    # Test CORS parsing
    exit_code = test_cors_parsing()
    
    sys.exit(exit_code)
