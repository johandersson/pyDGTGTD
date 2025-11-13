#!/bin/bash
# Unix/Linux/macOS shell script to set up the virtual environment

echo "Setting up wxGTD virtual environment..."
python3 setup_venv.py

if [ $? -eq 0 ]; then
    echo ""
    echo "Setup completed successfully!"
    echo ""
    echo "To activate the virtual environment, run:"
    echo "  source venv/bin/activate"
    echo ""
else
    echo ""
    echo "Setup failed! Please check the error messages above."
    echo ""
    exit 1
fi
