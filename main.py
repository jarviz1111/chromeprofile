"""
Browser Session Manager
-----------------------
A GUI application for managing browser sessions, profiles, and automating browser interactions.
"""
import os
import sys
from gui.app import BrowserSessionManagerApp

def main():
    """Main entry point for the Browser Session Manager application."""
    app = BrowserSessionManagerApp()
    app.run()

if __name__ == "__main__":
    main()
