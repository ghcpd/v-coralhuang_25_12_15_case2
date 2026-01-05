#!/usr/bin/env python3
"""
Test runner script for refactored tools.

This script executes the test suite and exits with appropriate status codes:
- 0: All tests passed
- 1: One or more tests failed
"""

import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from test_refactored import run_tests

if __name__ == "__main__":
    exit_code = run_tests()
    sys.exit(exit_code)
