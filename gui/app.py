"""
Main Application GUI Module
--------------------------
Defines the main application window and core functionality.
"""
import os
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
import csv

from browser_manager.session import SessionManager
from browser_manager.driver import BrowserDriver
from browser_manager.api import APIManager
from gui.components import create_header, create_api_frame, create_file_frame, create_proxy_frame
from gui.components import create_buttons_frame, create_log_frame
from utils.logger import TextLogger
from utils.system import kill_chrome_processes

class BrowserSessionManagerApp:
    """Main application for Browser Session Manager."""
    
    def __init__(self):
        """Initialize the application."""
        # Initialize managers
        self.session_manager = SessionManager(db_path='browser_sessions.db')
        self.api_manager = APIManager()
        self.browser_driver = BrowserDriver(self.session_manager)
        
        # App state
        self.profiles_list = []
        self.current_index = -1
        
        # Configure app appearance
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Create main window
        self.root = ctk.CTk()
        self.root.title("Browser Session Manager")
        self.root.geometry("800x700")
        self.root.configure(fg_color="#2b2b2b")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Variables
        self.file_path_var = tk.StringVar()
        self.proxy_var = tk.StringVar()
        self.api_user_id_var = tk.StringVar()
        self.api_key_var = tk.StringVar()
        
        # Build UI
        self._build_ui()
    
    def _build_ui(self):
        """Build the user interface."""
        # Main frame
        self.main_frame = ctk.CTkFrame(self.root, fg_color="#2b2b2b")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        create_header(self.main_frame)
        
        # API Credentials frame
        self.credentials_frame = create_api_frame(
            self.main_frame, 
            self.api_user_id_var, 
            self.api_key_var
        )
        
        # File selection frame
        self.file_frame = create_file_frame(
            self.main_frame, 
            self.file_path_var, 
            self.browse_file
        )
        
        # Proxy frame
        self.proxy_frame = create_proxy_frame(
            self.main_frame, 
            self.proxy_var
        )
        
        # Buttons frame
        self.buttons_frame = create_buttons_frame(
            self.main_frame, 
            start_command=lambda: threading.Thread(target=self.run_process).start(),
            skip_command=lambda: threading.Thread(target=self.run_next_profile).start()
        )
        
        # Log frame
        self.log_frame, self.log_text = create_log_frame(self.main_frame)
        
        # Redirect stdout to log text widget
        sys.stdout = TextLogger(self.log_text)
    
    def browse_file(self):
        """Open file dialog to select CSV file."""
        path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if path:
            self.file_path_var.set(path)
    
    def load_profiles(self, csv_path, override_proxy):
        """Load profiles from CSV file.
        
        Args:
            csv_path (str): Path to CSV file containing profiles.
            override_proxy (str): Global proxy to use for all profiles.
        """
        self.profiles_list = []
        try:
            with open(csv_path, newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    profile_id = row.get('profile_id', '').strip()
                    if not profile_id:
                        continue
                    
                    proxy = override_proxy if override_proxy else (row.get('proxy', '') or '').strip()
                    proxy = proxy if proxy else None
                    self.profiles_list.append((profile_id, proxy))
            
            print(f"✅ Loaded {len(self.profiles_list)} profiles from CSV.")
        except Exception as e:
            print(f"❌ CSV Load Error: {e}")
            messagebox.showerror("Error", f"Failed to load CSV file: {e}")
    
    def run_process(self):
        """Start the profile processing."""
        csv_path = self.file_path_var.get()
        proxy_input = self.proxy_var.get().strip()
        api_user_id = self.api_user_id_var.get().strip()
        api_key_id = self.api_key_var.get().strip()
        
        # Validate inputs
        if not os.path.exists(csv_path):
            messagebox.showerror("Error", "CSV file not found.")
            return
        
        if not api_user_id or not api_key_id:
            messagebox.showerror("Error", "API credentials are required.")
            return
        
        # Verify API credentials
        print("🔑 Verifying API credentials...")
        if not self.api_manager.verify_credentials(api_user_id, api_key_id):
            messagebox.showerror("Access Denied", "Invalid API credentials.")
            return
        
        print("✅ API credentials verified.")
        
        # Reset state
        self.current_index = -1
        
        # Load profiles and start processing
        self.load_profiles(csv_path, proxy_input)
        self.run_next_profile()
    
    def run_next_profile(self):
        """Process the next profile in the list."""
        # Close previous browser session
        if self.browser_driver.driver:
            try:
                # Save current session before closing
                self.browser_driver.save_current_session()
                self.browser_driver.close()
            except Exception as e:
                print(f"⚠️ Error closing browser: {e}")
            
            # Ensure Chrome processes are killed
            kill_chrome_processes()
        
        self.current_index += 1
        
        if self.current_index < len(self.profiles_list):
            profile_id, proxy = self.profiles_list[self.current_index]
            print(f"\n🚀 Starting profile {self.current_index + 1}/{len(self.profiles_list)}: {profile_id}")
            print(f"🌐 Proxy: {proxy or 'None'}")
            
            try:
                success = self.browser_driver.launch(profile_id, proxy)
                if not success:
                    print(f"❌ Failed to launch browser for {profile_id}, skipping...")
                    self.run_next_profile()  # Skip to next profile
            except Exception as e:
                print(f"❌ Error launching browser for {profile_id}: {e}")
                self.run_next_profile()  # Skip to next profile
        else:
            print("✅ All profiles processed.")
    
    def on_close(self):
        """Handle window close event."""
        try:
            # Clean up resources
            if self.browser_driver:
                self.browser_driver.close()
            
            # Restore stdout
            sys.stdout = sys.__stdout__
            
            # Kill any remaining Chrome processes
            kill_chrome_processes()
            
            # Destroy window
            self.root.destroy()
        except Exception as e:
            print(f"Error during cleanup: {e}")
            self.root.destroy()
    
    def run(self):
        """Run the application."""
        print("🚀 Browser Session Manager started.")
        print("Please select a CSV file with profiles and enter your API credentials.")
        self.root.mainloop()
