#!/bin/bash
# Fix decouple package installation
# This script removes the wrong 'decouple' package and installs 'python-decouple'

cd "$(dirname "$0")"
source venv/bin/activate

echo "Removing incorrect 'decouple' package..."
pip uninstall -y decouple

echo "Installing 'python-decouple'..."
pip install python-decouple

echo "Verifying installation..."
python -c "from decouple import config; print('✓ python-decouple installed successfully')"

echo ""
echo "Done! You can now run your Django project."
