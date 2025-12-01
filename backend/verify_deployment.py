#!/usr/bin/env python3
"""
Deployment Verification Script
Run this after deployment to verify everything is working correctly.

Usage:
    python verify_deployment.py https://your-backend.onrender.com
"""

import sys
import requests
from typing import Dict, List, Tuple


def test_endpoint(url: str, endpoint: str, expected_status: int = 200) -> Tuple[bool, str]:
    """Test a single endpoint."""
    full_url = f"{url}{endpoint}"
    try:
        response = requests.get(full_url, timeout=10)
        if response.status_code == expected_status:
            return True, f"✅ {endpoint} - OK ({response.status_code})"
        else:
            return False, f"❌ {endpoint} - Expected {expected_status}, got {response.status_code}"
    except requests.exceptions.RequestException as e:
        return False, f"❌ {endpoint} - Error: {str(e)}"


def verify_deployment(base_url: str) -> None:
    """Verify all critical endpoints."""
    print(f"\n🔍 Verifying deployment at: {base_url}\n")
    
    # Remove trailing slash
    base_url = base_url.rstrip('/')
    
    # Define test cases
    tests = [
        ("/", 200, "Root endpoint"),
        ("/docs", 200, "API documentation"),
        ("/api/v1/health", 200, "Health check"),
        ("/api/v1/auth/google", 200, "Google OAuth endpoint"),
    ]
    
    results: List[Tuple[bool, str]] = []
    
    # Run tests
    for endpoint, expected_status, description in tests:
        success, message = test_endpoint(base_url, endpoint, expected_status)
        results.append((success, message))
        print(message)
    
    # Summary
    print("\n" + "="*60)
    passed = sum(1 for success, _ in results if success)
    total = len(results)
    
    if passed == total:
        print(f"✅ All tests passed! ({passed}/{total})")
        print("\n🎉 Your backend is deployed and working correctly!")
        print("\nNext steps:")
        print("1. Update your Vercel frontend VITE_API_URL")
        print("2. Test login from frontend")
        print("3. Monitor logs in Render dashboard")
    else:
        print(f"⚠️  Some tests failed ({passed}/{total} passed)")
        print("\nTroubleshooting:")
        print("1. Check Render service logs")
        print("2. Verify environment variables")
        print("3. Ensure database migrations ran")
        print("4. Check CORS settings")
    
    print("="*60 + "\n")


def main():
    """Main entry point."""
    if len(sys.argv) != 2:
        print("Usage: python verify_deployment.py https://your-backend.onrender.com")
        sys.exit(1)
    
    base_url = sys.argv[1]
    
    if not base_url.startswith(('http://', 'https://')):
        print("❌ Error: URL must start with http:// or https://")
        sys.exit(1)
    
    verify_deployment(base_url)


if __name__ == "__main__":
    main()
