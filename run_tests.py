#!/usr/bin/env python3
"""
Test runner script for the Product Listing System
"""

import subprocess
import sys
import os


def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n{'='*50}")
    print(f"Running: {description}")
    print(f"Command: {command}")
    print(f"{'='*50}")

    result = subprocess.run(command, shell=True, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"❌ {description} failed!")
        print(f"Error: {result.stderr}")
        return False
    else:
        print(f"✅ {description} passed!")
        if result.stdout:
            print(result.stdout)
        return True


def main():
    """Main test runner"""
    print("🚀 Starting Product Listing System Test Suite")

    # Check if we're in the right directory
    if not os.path.exists("app/main.py"):
        print("❌ Error: Please run this script from the project root directory")
        sys.exit(1)

    # Test commands
    tests = [
        ("python -m pytest tests/ -v", "Unit Tests"),
        ("python -m pytest tests/ --cov=app --cov-report=html", "Coverage Report"),
        ("python -m flake8 app/ tests/", "Code Quality (Flake8)"),
        (
            "python -c 'import app.main; print(\"✅ App imports successfully\")'",
            "Import Test",
        ),
    ]

    # Run tests
    passed = 0
    total = len(tests)

    for command, description in tests:
        if run_command(command, description):
            passed += 1

    # Summary
    print(f"\n{'='*50}")
    print(f"Test Summary: {passed}/{total} test suites passed")
    print(f"{'='*50}")

    if passed == total:
        print("🎉 All tests passed!")
        sys.exit(0)
    else:
        print("❌ Some tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()

