#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Run all tests for wxGTD.

This script runs the test suite using pytest and generates coverage reports.

Usage:
    python run_tests.py              # Run all tests
    python run_tests.py -v           # Verbose output
    python run_tests.py -k test_task # Run specific tests
    python run_tests.py --cov        # Generate coverage report

Copyright (c) Karol Będkowski, 2013-2025
License: GPLv2+
"""

import sys
import os
import subprocess


def main():
    """Run the test suite."""
    # Add the project root to the Python path
    project_root = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, project_root)
    
    # Default pytest arguments
    pytest_args = [
        'pytest',
        'tests/',
        '-v',
        '--tb=short',
    ]
    
    # Add any command-line arguments
    if len(sys.argv) > 1:
        pytest_args.extend(sys.argv[1:])
    else:
        # If no arguments, add coverage
        pytest_args.extend([
            '--cov=wxgtd',
            '--cov-report=term-missing',
            '--cov-report=html',
        ])
    
    print("Running tests with arguments:", ' '.join(pytest_args))
    print("=" * 70)
    
    # Run pytest
    result = subprocess.run(pytest_args)
    
    if result.returncode == 0:
        print("\n" + "=" * 70)
        print("All tests passed!")
        if '--cov' in pytest_args or '--cov=wxgtd' in pytest_args:
            print("\nCoverage report generated in htmlcov/index.html")
    else:
        print("\n" + "=" * 70)
        print("Some tests failed.")
        sys.exit(1)


if __name__ == '__main__':
    main()
