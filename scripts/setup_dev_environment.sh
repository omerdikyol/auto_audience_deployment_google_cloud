#!/bin/bash
# Script to set up the development environment for the Audience Deployment Automation System

# Exit on error
set -e

echo "Setting up development environment for Audience Deployment Automation System..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install Python 3.9 or higher."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 9 ]); then
    echo "Python 3.9 or higher is required. You have Python $PYTHON_VERSION."
    exit 1
fi

echo "Using Python $PYTHON_VERSION"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "Please edit .env file with your API credentials."
fi

# Run tests to verify setup
echo "Running tests to verify setup..."
python run_tests.py || {
    echo "Some tests failed. This is expected if you haven't configured your .env file yet."
    echo "Please edit your .env file with valid credentials before running the tests again."
}

echo "Development environment setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit the .env file with your API credentials"
echo "2. Run 'source venv/bin/activate' to activate the virtual environment"
echo "3. Run 'python run_tests.py' to run the tests"
echo ""
echo "For deployment instructions, see docs/gcp_deployment.md"
