#!/bin/bash
# Run tests for wxGTD
# This script activates the virtual environment and runs tests

echo "Activating virtual environment..."
source venv/bin/activate

echo ""
echo "Running tests..."
python run_tests.py "$@"

echo ""
echo "Tests complete."
