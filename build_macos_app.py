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

# Global variable to track PyInstaller command method
USE_PYTHON_MODULE = False

def check_venv_packages(venv_path):
    """Check if virtual environment has required packages"""
    if not venv_path.exists():
        return False
    
    try:
        # Activate the virtual environment
        activate_script = venv_path / "bin" / "activate_this.py"
        if activate_script.exists():
            exec(activate_script.read_text(), {'__file__': str(activate_script)})
            
            # Check if required packages are available
            import PySide6
            import pyperclip
            print(f"✅ Virtual environment ready: {venv_path}")
            return True
        else:
            print(f"⚠️  Virtual environment exists but missing activation script: {venv_path}")
            return False
    except ImportError as e:
        print(f"⚠️  Virtual environment exists but missing packages: {venv_path}")
        print(f"   Missing: {e}")
        return False
    except Exception as e:
        print(f"⚠️  Error checking virtual environment {venv_path}: {e}")
        return False

def install_required_packages():
    """Install required packages in current environment"""
    print("📦 Installing required packages...")
    try:
        import subprocess
        result = subprocess.run([sys.executable, "-m", "pip", "install", "PySide6", "pyperclip", "pyinstaller"], 
                              capture_output=True, text=True, check=True)
        print("✅ Required packages installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install packages: {e}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return False

def create_local_venv():
    """Create and setup local virtual environment"""
    print("🏗️  Creating local virtual environment...")
    
    try:
        # Check if python3 is available
        result = subprocess.run(["python3", "--version"], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ python3 not found. Please install Python 3.8+")
            return False
        
        print(f"✅ Found Python: {result.stdout.strip()}")
        
        # Create virtual environment
        result = subprocess.run(["python3", "-m", "venv", ".venv"], capture_output=True, text=True, check=True)
        print("✅ Local virtual environment created")
        
        # Activate and install packages
        activate_script = Path(".venv") / "bin" / "activate_this.py"
        if activate_script.exists():
            exec(activate_script.read_text(), {'__file__': str(activate_script)})
            if install_required_packages():
                print("✅ Local virtual environment ready")
                return True
            else:
                print("❌ Failed to setup local virtual environment")
                return False
        else:
            print("❌ Failed to create local virtual environment")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create local virtual environment: {e}")
        return False
    except Exception as e:
        print(f"❌ Error creating local virtual environment: {e}")
        return False

def use_system_python():
    """Use system Python with user packages"""
    print("🐍 Using system Python with user packages...")
    
    try:
        # Check if python3 is available
        result = subprocess.run(["python3", "--version"], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ python3 not found. Please install Python 3.8+")
            return False
        
        print(f"✅ Found Python: {result.stdout.strip()}")
        
        # Try to install packages for current user
        print("📦 Installing packages for current user...")
        
        # Try pip3 first
        try:
            result = subprocess.run(["pip3", "install", "--user", "PySide6", "pyperclip", "pyinstaller"], 
                                  capture_output=True, text=True, check=True)
            print("✅ User packages installed successfully with pip3")
            return True
        except subprocess.CalledProcessError:
            pass
        
        # Try pip as fallback
        try:
            result = subprocess.run(["pip", "install", "--user", "PySide6", "pyperclip", "pyinstaller"], 
                                  capture_output=True, text=True, check=True)
            print("✅ User packages installed successfully with pip")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install user packages: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Error using system Python: {e}")
        return False

def detect_python_environment():
    """Detect and setup Python environment using multiple strategies"""
    print("🔍 Detecting Python environment...")
    
    # Strategy 1: Check if parent .venv exists and has packages
    parent_work_dir = Path(__file__).parent.parent.parent
    parent_venv_path = parent_work_dir / ".venv"
    
    if check_venv_packages(parent_venv_path):
        print(f"📁 Using parent virtual environment: {parent_venv_path}")
        activate_script = parent_venv_path / "bin" / "activate_this.py"
        exec(activate_script.read_text(), {'__file__': str(activate_script)})
        return True
    
    # Strategy 2: Check if local .venv exists and has packages
    local_venv_path = Path(".venv")
    if check_venv_packages(local_venv_path):
        print(f"📁 Using local virtual environment: .venv")
        activate_script = local_venv_path / "bin" / "activate_this.py"
        exec(activate_script.read_text(), {'__file__': str(activate_script)})
        return True
    
    # Strategy 3: Create local .venv
    if create_local_venv():
        print("📁 Using newly created local virtual environment")
        return True
    
    # Strategy 4: Use system Python with user packages
    if use_system_python():
        print("🐍 Using system Python with user packages")
        return True
    
    # All strategies failed
    print("❌ Failed to setup any Python environment")
    print("❌ Please ensure Python 3.8+ and pip are installed")
    return False

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
    global USE_PYTHON_MODULE
    
    print("🚀 Building Forever Clipboard macOS App")
    print("======================================")
    
    try:
        # Detect and setup Python environment using multiple strategies
        if not detect_python_environment():
            return 1
        
        # Check if PyInstaller is available
        try:
            import PyInstaller
            print(f"✅ PyInstaller found: {PyInstaller.__version__}")
        except ImportError:
            print("❌ PyInstaller not found. Installing...")
            if install_required_packages():
                print("✅ PyInstaller installed successfully")
            else:
                print("❌ Failed to install PyInstaller")
                return 1
        
        # Verify PyInstaller command is available
        try:
            result = subprocess.run(["pyinstaller", "--version"], capture_output=True, text=True, check=True)
            print(f"✅ PyInstaller command available: {result.stdout.strip()}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("⚠️  PyInstaller command not in PATH, using python -m PyInstaller")
            # Update the build command to use python -m PyInstaller
            global USE_PYTHON_MODULE
            USE_PYTHON_MODULE = True
        
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
        
        # Choose PyInstaller command based on availability
        if USE_PYTHON_MODULE:
            pyinstaller_cmd = f"{sys.executable} -m PyInstaller"
        else:
            pyinstaller_cmd = "pyinstaller"
        
        build_command = f"""{pyinstaller_cmd} --name=ForeverClipboard \
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