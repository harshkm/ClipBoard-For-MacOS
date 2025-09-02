#!/usr/bin/env python3
"""
Build Script for Forever Clipboard macOS App
This script packages the Python application into a proper macOS app bundle.
Uses the main .venv from the work_dir.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def get_main_venv_path():
    """Get the path to the main .venv in work_dir"""
    # Navigate up from current directory to find main work_dir
    current_dir = Path(__file__).parent
    work_dir = current_dir.parent.parent  # Go up two levels
    venv_path = work_dir / ".venv"
    
    if not venv_path.exists():
        raise FileNotFoundError(f"Main virtual environment not found at: {venv_path}")
    
    return venv_path

def run_command(command, cwd=None):
    """Run a shell command and return the result"""
    print(f"🔄 Running: {command}")
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            cwd=cwd, 
            capture_output=True, 
            text=True, 
            check=True
        )
        print(f"✅ Command successful")
        if result.stdout:
            print(f"Output: {result.stdout}")
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed with exit code {e.returncode}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        raise

def main():
    """Main build function"""
    print("🚀 Building Forever Clipboard macOS App")
    print("======================================")
    
    try:
        # Get the main .venv path
        venv_path = get_main_venv_path()
        print(f"📁 Using main virtual environment: {venv_path}")
        
        # Activate the main .venv
        activate_script = venv_path / "bin" / "activate_this.py"
        if activate_script.exists():
            exec(activate_script.read_text(), {'__file__': str(activate_script)})
            print("✅ Main virtual environment activated")
        else:
            print("⚠️  Could not activate virtual environment, continuing...")
        
        # Check if PyInstaller is available
        try:
            import PyInstaller
            print(f"✅ PyInstaller found: {PyInstaller.__version__}")
        except ImportError:
            print("❌ PyInstaller not found. Installing...")
            run_command(f"source {venv_path}/bin/activate && pip install pyinstaller")
        
        # Clean up previous builds
        print("🧹 Cleaning up previous builds...")
        for path in ["dist", "build"]:
            if os.path.exists(path):
                shutil.rmtree(path)
                print(f"✅ Removed {path}")
        
        # Build the app
        print("🔨 Building macOS app bundle...")
        
        # Check if custom icon exists
        icon_path = "clipboard-app-for-mac/icon.icns"
        icon_arg = f"--icon={icon_path}" if os.path.exists(icon_path) else ""
        
        build_command = f"""pyinstaller --name=ForeverClipboard \
            --windowed \
            --onedir \
            --add-data=clipboard-app-for-mac:clipboard-app-for-mac \
            --hidden-import=PySide6.QtCore \
            --hidden-import=PySide6.QtWidgets \
            --hidden-import=PySide6.QtGui \
            --hidden-import=pyperclip \
            {icon_arg} \
            clipboard-app-for-mac/clipboard_manager_gui.py"""
        
        run_command(build_command)
        
        # Copy the app bundle to the project directory
        print("📱 Setting up app bundle...")
        if os.path.exists("dist/ForeverClipboard.app"):
            # Remove existing app bundle
            if os.path.exists("ForeverClipboard.app"):
                shutil.rmtree("ForeverClipboard.app")
            
            # Copy new app bundle
            shutil.copytree("dist/ForeverClipboard.app", "ForeverClipboard.app")
            
            # Make executable
            os.chmod("ForeverClipboard.app/Contents/MacOS/ForeverClipboard", 0o755)
            
            print("✅ App bundle created successfully!")
            print(f"📁 Location: {os.path.abspath('ForeverClipboard.app')}")
        else:
            print("❌ App bundle not found in dist directory")
            return 1
        
        # Clean up build artifacts
        print("🧹 Cleaning up build artifacts...")
        for path in ["dist", "build"]:
            if os.path.exists(path):
                shutil.rmtree(path)
                print(f"✅ Removed {path}")
        
        print("")
        print("🎉 Build completed successfully!")
        print("📱 Your app is ready: ForeverClipboard.app")
        print("🚀 To launch: open ForeverClipboard.app")
        
        return 0
        
    except Exception as e:
        print(f"❌ Build failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
