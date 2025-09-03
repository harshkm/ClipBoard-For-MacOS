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

# Function to check if virtual environment has required packages
check_venv_packages() {
    local venv_path="$1"
    if [[ -d "$venv_path" ]]; then
        source "$venv_path/bin/activate"
        if python -c "import PySide6, pyperclip" 2>/dev/null; then
            print_success "Virtual environment ready: $venv_path"
            return 0
        else
            print_warning "Virtual environment exists but missing packages: $venv_path"
            return 1
        fi
    fi
    return 1
}

# Function to install packages in current environment
install_required_packages() {
    print_status "Installing required packages..."
    if pip install PySide6 pyperclip pyinstaller; then
        print_success "Required packages installed successfully"
        return 0
    else
        print_error "Failed to install packages with pip"
        return 1
    fi
}

# Function to create and setup local virtual environment
create_local_venv() {
    print_status "Creating local virtual environment..."
    
    # Check if python3 is available
    if ! command -v python3 &> /dev/null; then
        print_error "python3 not found. Please install Python 3.8+"
        exit 1
    fi
    
    # Create virtual environment
    if python3 -m venv .venv; then
        print_success "Local virtual environment created"
        
        # Activate and install packages
        source .venv/bin/activate
        if install_required_packages; then
            print_success "Local virtual environment ready"
            return 0
        else
            print_error "Failed to setup local virtual environment"
            return 1
        fi
    else
        print_error "Failed to create local virtual environment"
        return 1
    fi
}

# Function to use system Python with user packages
use_system_python() {
    print_status "Using system Python with user packages..."
    
    # Check if python3 is available
    if ! command -v python3 &> /dev/null; then
        print_error "python3 not found. Please install Python 3.8+"
        exit 1
    fi
    
    # Check if pip3 is available
    if ! command -v pip3 &> /dev/null; then
        print_error "pip3 not found. Please install pip"
        exit 1
    fi
    
    # Install packages for current user
    print_status "Installing packages for current user..."
    if pip3 install --user PySide6 pyperclip pyinstaller; then
        print_success "User packages installed successfully"
        return 0
    fi
    
    # Try alternative pip command
    if pip install --user PySide6 pyperclip pyinstaller; then
        print_success "User packages installed successfully"
        return 0
    else
        print_error "Failed to install user packages"
        return 1
    fi
}

# Determine Python environment strategy
PYTHON_CMD=""
VENV_ACTIVATED=false

print_status "Detecting Python environment..."

# Strategy 1: Check if parent .venv exists and has packages
PARENT_WORK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PARENT_VENV_PATH="$PARENT_WORK_DIR/.venv"

if check_venv_packages "$PARENT_VENV_PATH"; then
    print_status "Using parent virtual environment: $PARENT_VENV_PATH"
    source "$PARENT_VENV_PATH/bin/activate"
    VENV_ACTIVATED=true
    PYTHON_CMD="python"
    
# Strategy 2: Check if local .venv exists and has packages
elif check_venv_packages ".venv"; then
    print_status "Using local virtual environment: .venv"
    source .venv/bin/activate
    VENV_ACTIVATED=true
    PYTHON_CMD="python"
    
# Strategy 3: Create local .venv
elif create_local_venv; then
    print_status "Using newly created local virtual environment"
    VENV_ACTIVATED=true
    PYTHON_CMD="python"
    
# Strategy 4: Use system Python with user packages
elif use_system_python; then
    print_status "Using system Python with user packages"
    PYTHON_CMD="python3"
    
else
    print_error "Failed to setup any Python environment"
    print_error "Please ensure Python 3.8+ and pip are installed"
    exit 1
fi

# Verify PyInstaller is available
if ! command -v pyinstaller &> /dev/null; then
    print_status "PyInstaller not found, installing..."
    if [[ "$VENV_ACTIVATED" == true ]]; then
        pip install pyinstaller
    else
        pip3 install --user pyinstaller
    fi
    
    if ! command -v pyinstaller &> /dev/null; then
        print_error "Failed to install PyInstaller"
        exit 1
    fi
fi

print_success "Python environment ready with all required packages"

# Create app icon if it doesn't exist
if [[ ! -f "clipboard-app-for-mac/icon.icns" ]]; then
    print_status "Creating app icon..."
    if [[ -f "create_icon.py" ]]; then
        $PYTHON_CMD create_icon.py
        print_success "App icon created"
    else
        print_warning "create_icon.py not found, skipping icon creation"
    fi
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
