"""
Logger Module
-----------
Handles logging to GUI and console.
"""
import sys
import tkinter as tk

class TextLogger:
    """Logger that redirects output to a tkinter text widget."""
    
    def __init__(self, textbox):
        """Initialize the logger with a text widget.
        
        Args:
            textbox: Tkinter text widget to log to.
        """
        self.textbox = textbox
    
    def write(self, msg):
        """Write a message to the text widget and console.
        
        Args:
            msg (str): Message to log.
        """
        self.textbox.insert(tk.END, msg)
        self.textbox.see(tk.END)
        sys.__stdout__.write(msg)
    
    def flush(self):
        """Flush the logger (required for compatibility)."""
        pass
