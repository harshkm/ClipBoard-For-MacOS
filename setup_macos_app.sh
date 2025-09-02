#!/bin/bash

# Forever Clipboard macOS App Setup Script
# This script sets up the entire macOS app development environment
# Uses the existing .venv in the main work_dir

set -e  # Exit on any error

echo "🚀 Forever Clipboard macOS App Setup"
echo "====================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}📋 $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if we're on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    print_error "This script must be run on macOS"
    exit 1
fi

# Get the main work_dir path (parent of current directory)
MAIN_WORK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
MAIN_VENV_PATH="$MAIN_WORK_DIR/.venv"

print_status "Using main work directory: $MAIN_WORK_DIR"
print_status "Using main virtual environment: $MAIN_VENV_PATH"

# Check if main .venv exists
if [[ ! -d "$MAIN_VENV_PATH" ]]; then
    print_error "Main virtual environment not found at: $MAIN_VENV_PATH"
    print_error "Please ensure you have a .venv in your main work_dir"
    exit 1
fi

# Check if main .venv has required packages
print_status "Checking main virtual environment packages..."
source "$MAIN_VENV_PATH/bin/activate"

if ! python -c "import PySide6, pyperclip" 2>/dev/null; then
    print_error "Required packages not found in main .venv"
    print_error "Please install: PySide6 and pyperclip"
    exit 1
fi

print_success "Main virtual environment is ready with required packages"

# Check if PyInstaller is available
if ! command -v pyinstaller &> /dev/null; then
    print_status "Installing PyInstaller in main .venv..."
    pip install pyinstaller
    print_success "PyInstaller installed"
else
    print_success "PyInstaller already available"
fi

# Create app icon if it doesn't exist
if [[ ! -f "clipboard-app-for-mac/icon.icns" ]]; then
    print_status "Creating app icon..."
    python create_icon.py
    print_success "App icon created"
else
    print_success "App icon already exists"
fi

# Clean up any previous builds
print_status "Cleaning up previous builds..."
rm -rf dist build
print_success "Previous builds cleaned up"

# Build the macOS app
print_status "Building macOS app bundle..."
pyinstaller --name=ForeverClipboard \
            --windowed \
            --onedir \
            --add-data=clipboard-app-for-mac:clipboard-app-for-mac \
            --hidden-import=PySide6.QtCore \
            --hidden-import=PySide6.QtWidgets \
            --hidden-import=PySide6.QtGui \
            --hidden-import=pyperclip \
            --icon=clipboard-app-for-mac/icon.icns \
            clipboard-app-for-mac/clipboard_manager_gui.py

if [[ $? -eq 0 ]]; then
    print_success "App bundle built successfully!"
else
    print_error "Failed to build app bundle"
    exit 1
fi

# Copy the app bundle to the project directory
print_status "Setting up app bundle..."
if [[ -d "dist/ForeverClipboard.app" ]]; then
    cp -r dist/ForeverClipboard.app .
    chmod +x ForeverClipboard.app/Contents/MacOS/ForeverClipboard
    print_success "App bundle copied to project directory"
else
    print_error "App bundle not found in dist directory"
    exit 1
fi

# Clean up build artifacts
print_status "Cleaning up build artifacts..."
rm -rf dist build
print_success "Build artifacts cleaned up"

echo ""
print_success "🎉 Forever Clipboard macOS App Setup Complete!"
echo ""
echo "📱 Your app is ready at: ForeverClipboard.app"
echo "🚀 To launch: open ForeverClipboard.app"
echo ""
