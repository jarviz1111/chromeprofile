"""
GUI Components Module
--------------------
Reusable GUI components for the application.
"""
import tkinter as tk
from tkinter import scrolledtext
import customtkinter as ctk

def create_header(parent):
    """Create header with title.
    
    Args:
        parent: Parent widget.
        
    Returns:
        ctk.CTkLabel: Header label widget.
    """
    title_label = ctk.CTkLabel(
        parent,
        text="Browser Session Manager",
        font=ctk.CTkFont(size=24, weight="bold"),
        text_color="#ffffff"
    )
    title_label.pack(pady=20)
    return title_label

def create_api_frame(parent, user_id_var, key_var):
    """Create frame for API credentials.
    
    Args:
        parent: Parent widget.
        user_id_var: StringVar for user ID.
        key_var: StringVar for API key.
        
    Returns:
        ctk.CTkFrame: API credentials frame.
    """
    # API Credentials Frame
    credentials_frame = ctk.CTkFrame(parent, fg_color="#363636")
    credentials_frame.pack(fill="x", padx=10, pady=10)
    
    # API User ID
    ctk.CTkLabel(
        credentials_frame,
        text="API User ID:",
        font=ctk.CTkFont(size=12),
        text_color="#ffffff"
    ).pack(pady=(10, 0))
    ctk.CTkEntry(
        credentials_frame,
        textvariable=user_id_var,
        width=400,
        height=35,
        font=ctk.CTkFont(size=12)
    ).pack(pady=5)
    
    # API Key
    ctk.CTkLabel(
        credentials_frame,
        text="API Key:",
        font=ctk.CTkFont(size=12),
        text_color="#ffffff"
    ).pack(pady=(10, 0))
    ctk.CTkEntry(
        credentials_frame,
        textvariable=key_var,
        width=400,
        height=35,
        font=ctk.CTkFont(size=12),
        show="*"
    ).pack(pady=5)
    
    return credentials_frame

def create_file_frame(parent, file_path_var, browse_command):
    """Create frame for file selection.
    
    Args:
        parent: Parent widget.
        file_path_var: StringVar for file path.
        browse_command: Command to execute when browse button is clicked.
        
    Returns:
        ctk.CTkFrame: File selection frame.
    """
    # File Selection Frame
    file_frame = ctk.CTkFrame(parent, fg_color="#363636")
    file_frame.pack(fill="x", padx=10, pady=10)
    
    ctk.CTkLabel(
        file_frame,
        text="Select CSV File:",
        font=ctk.CTkFont(size=12),
        text_color="#ffffff"
    ).pack(pady=(10, 0))
    
    file_entry_frame = ctk.CTkFrame(file_frame, fg_color="transparent")
    file_entry_frame.pack(fill="x", padx=10, pady=5)
    
    ctk.CTkEntry(
        file_entry_frame,
        textvariable=file_path_var,
        width=300,
        height=35,
        font=ctk.CTkFont(size=12)
    ).pack(side="left", padx=(0, 10))
    
    ctk.CTkButton(
        file_entry_frame,
        text="Browse",
        command=browse_command,
        width=100,
        height=35,
        font=ctk.CTkFont(size=12)
    ).pack(side="left")
    
    return file_frame

def create_proxy_frame(parent, proxy_var):
    """Create frame for proxy configuration.
    
    Args:
        parent: Parent widget.
        proxy_var: StringVar for proxy.
        
    Returns:
        ctk.CTkFrame: Proxy configuration frame.
    """
    # Proxy Frame
    proxy_frame = ctk.CTkFrame(parent, fg_color="#363636")
    proxy_frame.pack(fill="x", padx=10, pady=10)
    
    ctk.CTkLabel(
        proxy_frame,
        text="Global Proxy (Optional):",
        font=ctk.CTkFont(size=12),
        text_color="#ffffff"
    ).pack(pady=(10, 0))
    ctk.CTkEntry(
        proxy_frame,
        textvariable=proxy_var,
        width=400,
        height=35,
        font=ctk.CTkFont(size=12),
        placeholder_text="Example: 123.456.789.012:8080 or user:pass@123.456.789.012:8080"
    ).pack(pady=5)
    
    return proxy_frame

def create_buttons_frame(parent, start_command, skip_command):
    """Create frame with action buttons.
    
    Args:
        parent: Parent widget.
        start_command: Command to execute when start button is clicked.
        skip_command: Command to execute when skip button is clicked.
        
    Returns:
        ctk.CTkFrame: Buttons frame.
    """
    # Buttons Frame
    buttons_frame = ctk.CTkFrame(parent, fg_color="transparent")
    buttons_frame.pack(fill="x", padx=10, pady=10)
    
    ctk.CTkButton(
        buttons_frame,
        text="Start Process",
        command=start_command,
        width=150,
        height=40,
        font=ctk.CTkFont(size=14, weight="bold")
    ).pack(side="left", padx=(0, 10))
    
    ctk.CTkButton(
        buttons_frame,
        text="Skip Profile",
        command=skip_command,
        width=150,
        height=40,
        font=ctk.CTkFont(size=14, weight="bold")
    ).pack(side="left", padx=(0, 10))
    
    return buttons_frame

def create_log_frame(parent):
    """Create frame for log display.
    
    Args:
        parent: Parent widget.
        
    Returns:
        tuple: (log_frame, log_text_widget)
    """
    # Log Frame
    log_frame = ctk.CTkFrame(parent, fg_color="#363636")
    log_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    ctk.CTkLabel(
        log_frame,
        text="Process Log:",
        font=ctk.CTkFont(size=12),
        text_color="#ffffff"
    ).pack(anchor="w", padx=10, pady=(10, 0))
    
    log_text = scrolledtext.ScrolledText(
        log_frame,
        width=80,
        height=15,
        font=("Consolas", 10),
        bg="#1e1e1e",
        fg="#ffffff",
        wrap=tk.WORD
    )
    log_text.pack(padx=10, pady=10, fill="both", expand=True)
    
    return log_frame, log_text
