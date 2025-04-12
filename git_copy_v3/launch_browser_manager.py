#!/usr/bin/env python3
"""
Browser Session Manager Launcher
--------------------------------
Provides a simple way to launch the Browser Session Manager application
with proper error handling and dependency checks.
"""
import sys
import os
import platform
import subprocess
import tkinter as tk
from tkinter import messagebox

def check_dependencies():
    """Check that all required dependencies are installed."""
    required_packages = [
        "customtkinter", 
        "undetected-chromedriver", 
        "selenium", 
        "fake-useragent",
        "psutil",
        "requests"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    return missing_packages

def install_dependencies(missing_packages):
    """Install missing dependencies."""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--user"] + missing_packages)
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    """Main launcher function."""
    # Check if browser_session_manager.py exists
    if not os.path.exists("browser_session_manager.py"):
        print("Error: browser_session_manager.py not found!")
        messagebox.showerror("Error", "browser_session_manager.py not found!\n\nPlease make sure you are running this script from the same directory as the Browser Session Manager files.")
        return 1
        
    # Check dependencies
    missing_packages = check_dependencies()
    if missing_packages:
        print(f"Installing missing dependencies: {', '.join(missing_packages)}")
        
        # Initialize Tkinter root window for messagebox
        root = tk.Tk()
        root.withdraw()  # Hide the root window
        
        # Ask user if they want to install missing packages
        if messagebox.askyesno("Dependencies Required", 
                               f"The following dependencies need to be installed:\n\n{', '.join(missing_packages)}\n\nDo you want to install them now?"):
            if install_dependencies(missing_packages):
                messagebox.showinfo("Success", "Dependencies installed successfully! The application will now start.")
            else:
                messagebox.showerror("Error", "Failed to install dependencies. Please install them manually using pip:\n\npip install " + " ".join(missing_packages))
                return 1
        else:
            messagebox.showinfo("Information", "The application requires these dependencies to run. Exiting.")
            return 1
            
        root.destroy()
    
    # Run the main application
    print("Starting Browser Session Manager...")
    result = subprocess.call([sys.executable, "browser_session_manager.py"])
    
    return result

if __name__ == "__main__":
    sys.exit(main())