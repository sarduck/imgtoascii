#!/usr/bin/env python3
import subprocess
import sys
import os
import platform

def check_python_version():
    # Check if Python version is 3.6+
    if sys.version_info < (3, 6):
        print("Error: Python 3.6 or higher is required.")
        sys.exit(1)
    print(f"✓ Python version: {sys.version.split()[0]}")

def install_requirements():
    # Install required packages
    try:
        print("Installing required packages...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Dependencies installed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error installing packages: {e}")
        sys.exit(1)

def create_desktop_shortcut():
    # Create desktop shortcut based on the platform
    system = platform.system()
    
    if system == "Windows":
        try:
            # Windows desktop path
            desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
            script_path = os.path.abspath("ascii_art_app.py")
            
            # Create a batch file
            shortcut_path = os.path.join(desktop_path, "ASCII Art Generator.bat")
            with open(shortcut_path, "w") as batch_file:
                batch_file.write(f'@echo off\n"{sys.executable}" "{script_path}"\n')
            
            print(f"✓ Desktop shortcut created at: {shortcut_path}")
        except Exception as e:
            print(f"Warning: Could not create desktop shortcut: {e}")
    
    elif system == "Linux":
        try:
            # Linux desktop path
            desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
            if not os.path.exists(desktop_path):
                desktop_path = os.path.join(os.path.expanduser("~"), ".local", "share", "applications")
                if not os.path.exists(desktop_path):
                    os.makedirs(desktop_path)
            
            script_path = os.path.abspath("ascii_art_app.py")
            
            # Create a .desktop file
            shortcut_path = os.path.join(desktop_path, "ascii-art-generator.desktop")
            with open(shortcut_path, "w") as desktop_file:
                desktop_file.write(f"""[Desktop Entry]
Version=1.0
Type=Application
Name=ASCII Art Generator
Comment=Convert images to ASCII art
Exec={sys.executable} {script_path}
Terminal=false
Categories=Graphics;Utility;
""")
            
            # Make it executable
            os.chmod(shortcut_path, 0o755)
            print(f"✓ Desktop shortcut created at: {shortcut_path}")
        except Exception as e:
            print(f"Warning: Could not create desktop shortcut: {e}")
    
    else:
        print("Desktop shortcut creation not supported on this platform.")

def main():
    print("ASCII Art Generator Setup")
    print("=" * 25)
    
    check_python_version()
    install_requirements()
    
    # Ask about desktop shortcut
    create_shortcut = input("Create desktop shortcut? (y/n): ").strip().lower()
    if create_shortcut == "y":
        create_desktop_shortcut()
    
    print("\nSetup completed successfully!")
    print("To run the application, use: python ascii_art_app.py")

if __name__ == "__main__":
    main() 