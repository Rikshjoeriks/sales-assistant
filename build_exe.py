#!/usr/bin/env python3
"""
Build script to create an executable for the Spec Matcher application
"""
import subprocess
import sys
import os
from pathlib import Path

def build_exe():
    """Build the executable using PyInstaller"""
    
    # Get the project directory
    project_dir = Path(__file__).parent
    
    print("🚀 Building Spec Matcher Executable...")
    print(f"📁 Project directory: {project_dir}")
    
    # PyInstaller command
    cmd = [
        "pyinstaller",
        "--onefile",                    # Single executable file
        "--windowed",                   # No console window (GUI app)
        "--name=SpecMatcher",          # Name of the executable
        "--icon=NONE",                 # No icon for now
        "--add-data=masterlists;masterlists",  # Include masterlists folder
        "--hidden-import=tkinter",     # Ensure tkinter is included
        "--hidden-import=sqlite3",     # Ensure sqlite3 is included
        "--hidden-import=openai",      # Ensure openai is included
        "--hidden-import=requests",    # Ensure requests is included
        "--clean",                     # Clean build
        "ui.py"                        # Main script
    ]
    
    print("🔨 Running PyInstaller...")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, cwd=project_dir, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Build successful!")
            print(f"📦 Executable created: {project_dir}/dist/SpecMatcher.exe")
            print("\n📋 Build completed successfully!")
            print("🎯 You can now run SpecMatcher.exe without Python installed")
            
            # Check if the file exists
            exe_path = project_dir / "dist" / "SpecMatcher.exe"
            if exe_path.exists():
                size_mb = exe_path.stat().st_size / (1024 * 1024)
                print(f"📊 Executable size: {size_mb:.1f} MB")
            
        else:
            print("❌ Build failed!")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error during build: {e}")
        return False
    
    return True

def create_launcher_script():
    """Create a simple launcher script"""
    launcher_content = '''@echo off
echo Starting Spec Matcher...
cd /d "%~dp0"
if exist "SpecMatcher.exe" (
    start "" "SpecMatcher.exe"
) else (
    echo SpecMatcher.exe not found!
    echo Please run build_exe.py first to create the executable.
    pause
)
'''
    
    with open("launch_spec_matcher.bat", "w") as f:
        f.write(launcher_content)
    
    print("✅ Created launch_spec_matcher.bat")

if __name__ == "__main__":
    print("🏗️  Spec Matcher Build Tool")
    print("=" * 40)
    
    if build_exe():
        create_launcher_script()
        print("\n🎉 All done! You now have:")
        print("   📦 SpecMatcher.exe (in dist/ folder)")
        print("   🚀 launch_spec_matcher.bat (quick launcher)")
        print("\n💡 To distribute: Copy the entire 'dist' folder to any Windows computer")
    else:
        print("\n💥 Build failed. Check the error messages above.")
        sys.exit(1)
