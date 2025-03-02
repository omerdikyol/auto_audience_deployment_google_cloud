#!/usr/bin/env python3
"""
Test runner script for the Audience Deployment Automation System.
Run this script to execute all unit tests.
"""

import unittest
import os
import sys

if __name__ == '__main__':
    # Add the project root directory to the Python path
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
    
    # Discover and run all tests
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('tests', pattern='test_*.py')
    
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)
    
    # Exit with non-zero code if tests failed
    sys.exit(not result.wasSuccessful())
