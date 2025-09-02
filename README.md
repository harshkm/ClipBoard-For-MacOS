# 🚀 Forever Clipboard - Build Instructions

This directory contains everything you need to build the Forever Clipboard macOS app from source code.

## 📋 What's Included

- **`clipboard-app-for-mac/`** - Complete source code
- **`setup_macos_app.sh`** - Main build script (recommended)
- **`build_macos_app.py`** - Alternative Python build script
- **`ForeverClipboard.app/`** - Built app bundle (after building)

## 🔧 Building the App

### **Option 1: Using the Main Build Script (Recommended)**

```bash
# Make sure you're in this directory
cd forever_clipboard_app_builder

# Run the build script
./setup_macos_app.sh
```

This script will:
- ✅ Check your Python environment
- ✅ Install required dependencies
- ✅ Build the macOS app bundle
- ✅ Create `ForeverClipboard.app`
- ✅ Clean up build artifacts

### **Option 2: Using the Python Build Script**

```bash
# Make sure you're in this directory
cd forever_clipboard_app_builder

# Run the Python build script
python build_macos_app.py
```

This script provides the same functionality but with more detailed output.

## 📱 After Building

Once the build completes successfully:

```bash
# Launch the app
open ForeverClipboard.app

# Or drag ForeverClipboard.app to your Applications folder
```

## 🛠️ Prerequisites

- **macOS**: 10.15 (Catalina) or later
- **Python**: 3.13+ with pip
- **Dependencies**: PySide6, pyperclip, PyInstaller

The build scripts will automatically check and install missing dependencies.

## 📚 Detailed Documentation

**IF YOU DONT WANT TO BUILD THE COMPLETE APP AND JUST KEEP IT AS A LIGHT WEIGHT TOOL**

**See: `clipboard-app-for-mac/README.md`**

This contains:
- Complete feature list
- User guide
- Development setup
- Troubleshooting
- Contributing guidelines

## 🚨 Troubleshooting

### **Build Fails**
- Ensure you have Python 3.13+ installed
- Check that you're in the correct directory
- Verify you have write permissions

### **App Won't Launch**
- First time: Right-click → Open (bypass Gatekeeper)
- Check Console.app for error messages
- Ensure macOS 10.15+ compatibility

## 🎯 Quick Start

```bash
# 1. Navigate to this directory
cd forever_clipboard_app_builder

# 2. Build the app
./setup_macos_app.sh

# 3. Launch the app
open ForeverClipboard.app
```

## 📁 Project Structure

```
forever_clipboard_app_builder/
├── README.md                    # This file (build instructions)
├── setup_macos_app.sh          # Main build script
├── build_macos_app.py          # Alternative build script
├── clipboard-app-for-mac/      # Source code + detailed README
└── ForeverClipboard.app/       # Built app (after building)
```

---

**Need help?** Check the detailed README in `clipboard-app-for-mac/README.md` for comprehensive information about the app and its features.
