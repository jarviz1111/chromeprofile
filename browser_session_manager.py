"""
Browser Session Manager
-----------------------
A comprehensive application for managing browser sessions, profiles, and automating browser interactions.
"""
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import csv
import os
import threading
import requests
import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from fake_useragent import UserAgent
import sqlite3
import json
import time
import random
from datetime import datetime
import sys
import psutil
import customtkinter as ctk
import platform
import argparse
import traceback
import threading
import itertools

# Constants
DB_PATH = 'browser_sessions.db'
LOGIN_URL = "https://accounts.google.com/signup"
BROWSER_PROFILES_DIR = "browser_profiles"
APP_VERSION = "1.0.0"

# Global variables
current_driver = None
profiles_list = []
current_index = -1
is_running = False
api_credentials_verified = False

class TextLogger:
    """Logger that redirects output to a tkinter text widget."""
    def __init__(self, textbox):
        """Initialize the logger with a text widget."""
        self.textbox = textbox

    def write(self, msg):
        """Write a message to the text widget and console."""
        if self.textbox:
            self.textbox.insert(tk.END, msg)
            self.textbox.see(tk.END)
        sys.__stdout__.write(msg)

    def flush(self):
        """Flush the logger (required for compatibility)."""
        pass

class DatabaseManager:
    """Manages database operations for browser sessions."""
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self.init_db()
        
    def init_db(self):
        """Initialize the database with required tables."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                c = conn.cursor()
                c.execute('''CREATE TABLE IF NOT EXISTS sessions (
                    profile TEXT PRIMARY KEY,
                    user_agent TEXT,
                    cookies TEXT,
                    updated_at TEXT
                )''')
                
                # Check if updated_at column exists
                c.execute("PRAGMA table_info(sessions)")
                columns = [col[1] for col in c.fetchall()]
                if 'updated_at' not in columns:
                    c.execute("ALTER TABLE sessions ADD COLUMN updated_at TEXT")
                conn.commit()
                print("✅ Database initialized successfully.")
        except Exception as e:
            print(f"❌ Database initialization error: {e}")
            
    def save_session(self, profile, user_agent, cookies):
        """Save browser session to the database."""
        try:
            with sqlite3.connect(self.db_path, timeout=10) as conn:
                c = conn.cursor()
                now = datetime.utcnow().isoformat()
                c.execute('''INSERT OR REPLACE INTO sessions 
                            (profile, user_agent, cookies, updated_at)
                            VALUES (?, ?, ?, ?)''',
                        (profile, user_agent, json.dumps(cookies), now))
                conn.commit()
            print(f"✅ Session saved for profile: {profile}")
            return True
        except Exception as e:
            print(f"❌ DB Save Error: {e}")
            return False
            
    def load_session(self, profile):
        """Load browser session from the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                c = conn.cursor()
                c.execute('SELECT user_agent, cookies FROM sessions WHERE profile = ?', (profile,))
                result = c.fetchone()
                if result:
                    cookies = json.loads(result[1]) if result[1] else None
                    return result[0], cookies
                return None, None
        except Exception as e:
            print(f"❌ DB Load Error: {e}")
            return None, None
            
    def get_all_profiles(self):
        """Get all profiles from the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                c = conn.cursor()
                c.execute('SELECT profile, updated_at FROM sessions ORDER BY updated_at DESC')
                return c.fetchall()
        except Exception as e:
            print(f"❌ DB Load Error: {e}")
            return []
            
    def delete_profile(self, profile):
        """Delete a profile from the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                c = conn.cursor()
                c.execute('DELETE FROM sessions WHERE profile = ?', (profile,))
                conn.commit()
                return True
        except Exception as e:
            print(f"❌ DB Delete Error: {e}")
            return False

class APIManager:
    """Handles API verification and authentication."""
    def __init__(self, api_base_url="https://inboxinnovations.org"):
        self.api_base_url = api_base_url
        
    def verify_credentials(self, user_id, key_id):
        """Verify API credentials against the verification endpoint."""
        try:
            if not user_id or not key_id:
                print("❌ API credentials cannot be empty")
                return False
                
            # For demonstration purposes only
            # In a real application, uncomment this and remove the following demo logic
            # api_link = f"{self.api_base_url}?menuname=seeding&userid={user_id}&keyid={key_id}"
            # response = requests.get(api_link, timeout=10)
            # return response.text.strip() == "1"
            
            # Demo mode - always accept non-empty credentials
            print("✅ API credentials accepted (DEMO MODE)")
            return True
            
        except Exception as e:
            print(f"❌ API verification failed: {e}")
            return False

class BrowserManager:
    """Manages browser session operations."""
    def __init__(self, db_manager, profiles_dir=BROWSER_PROFILES_DIR):
        self.db_manager = db_manager
        self.profiles_dir = profiles_dir
        os.makedirs(profiles_dir, exist_ok=True)
        
    def generate_user_agent(self):
        """Generate a desktop user agent string."""
        try:
            ua = UserAgent()
            for _ in range(10):
                candidate = ua.chrome
                if all(x not in candidate.lower() for x in ['mobile', 'android', 'iphone', 'ipad']):
                    return candidate
            # Fallback user agent if no suitable one found
            return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        except Exception as e:
            print(f"⚠️ Error loading fake_useragent: {e}")
            return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            
    def kill_chrome_processes(self):
        """Kill all running Chrome and ChromeDriver processes."""
        try:
            for proc in psutil.process_iter():
                try:
                    if proc.name().lower() in ["chrome.exe", "chromedriver.exe", "chrome", "chromedriver"]:
                        proc.kill()
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
        except Exception as e:
            print(f"⚠️ Error killing Chrome processes: {e}")
            
    def launch_browser(self, profile_id, proxy=None):
        """Launch a browser session with the specified profile."""
        print(f"🟢 Launching browser for profile: {profile_id}")
        
        # Set up profile directory
        # First check if C:/temp exists and is writable (Windows-specific path)
        if platform.system() == 'Windows' and os.path.exists('C:/') and os.access('C:/', os.W_OK):
            try:
                os.makedirs(f"C:/temp", exist_ok=True)
                user_data_dir = f"C:/temp/{profile_id}"
                print(f"🟢 Using Windows temp directory: {user_data_dir}")
            except Exception as e:
                print(f"⚠️ Could not create Windows temp directory: {e}")
                user_data_dir = os.path.join(self.profiles_dir, profile_id)
                print(f"🟡 Using default profile directory: {user_data_dir}")
        else:
            # Use the default profiles directory
            user_data_dir = os.path.join(self.profiles_dir, profile_id)
            print(f"🟡 Using default profile directory: {user_data_dir}")
            
        os.makedirs(user_data_dir, exist_ok=True)
        
        # Get stored session data
        stored_user_agent, stored_cookies = self.db_manager.load_session(profile_id)
        
        # Use stored user agent or generate a new one
        user_agent = stored_user_agent if stored_user_agent else self.generate_user_agent()
        
        # Configure Chrome options
        options = uc.ChromeOptions()
        options.add_argument(f"--user-agent={user_agent}")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-extensions")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument(f"--user-data-dir={user_data_dir}")
        
        # Add proxy if specified
        if proxy:
            options.add_argument(f"--proxy-server=http://{proxy}")
            print(f"🌐 Using Proxy: {proxy}")
        else:
            print("🚫 No proxy set.")
            
        # Initialize Chrome driver
        custom_driver_path = "c/chromedriver.exe"
        
        # Check if custom driver exists
        if os.path.exists(custom_driver_path):
            print(f"🔍 Using custom chromedriver from: {custom_driver_path}")
            try:
                driver = uc.Chrome(options=options, driver_executable_path=custom_driver_path)
            except Exception as e:
                print(f"❌ Failed to launch Chrome with custom driver: {e}")
                print("⚠️ Trying with default chromedriver...")
                try:
                    driver = uc.Chrome(options=options, use_subprocess=True)
                except:
                    raise  # Re-raise exception if still failing
        else:
            print("🔍 Custom chromedriver not found, using default")
            try:
                driver = uc.Chrome(options=options)
            except Exception as e:
                print(f"❌ Failed to launch Chrome: {e}")
                print("⚠️ Trying with default chromedriver in subprocess mode...")
                try:
                    driver = uc.Chrome(options=options, use_subprocess=True)
                except:
                    raise  # Re-raise exception if still failing
                
        # Apply anti-detection measures
        self._apply_anti_detection(driver, user_agent)
        
        # Load cookies if available, otherwise navigate to login page
        if stored_cookies:
            print("🟡 Loading cookies...")
            driver.get("https://accounts.google.com/")
            for cookie in stored_cookies:
                if 'sameSite' in cookie:
                    del cookie['sameSite']
                try:
                    driver.add_cookie(cookie)
                except Exception as cookie_error:
                    print(f"⚠️ Cookie error: {cookie_error}")
            driver.get("https://mail.google.com/")
        else:
            print("🟢 No cookies found. Creating new session...")
            driver.get(LOGIN_URL)
            print("⚠️ Please login manually...")
            time.sleep(5)  # Wait a bit for the page to load
        
        return driver, user_agent
        
    def _apply_anti_detection(self, driver, user_agent):
        """Apply anti-fingerprinting measures to make automation less detectable."""
        # Override user agent for more thorough masking
        driver.execute_cdp_cmd('Network.setUserAgentOverride', {
            "userAgent": user_agent,
            "acceptLanguage": "en-US,en;q=0.9",
            "platform": "Win32"
        })
        
        # Hide WebDriver property
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        # Randomize WebGL fingerprint
        vendor_renderer_pairs = [
            ('Intel Inc.', 'Intel Iris Xe Graphics'),
            ('Intel Inc.', 'Intel UHD Graphics 630'),
            ('Intel Inc.', 'Intel HD Graphics 520'),
            ('Intel Inc.', 'Intel Iris Plus Graphics 655'),
            ('Intel Inc.', 'Intel UHD Graphics 620'),
            ('NVIDIA Corporation', 'NVIDIA GeForce GTX 1050'),
            ('NVIDIA Corporation', 'NVIDIA GeForce GTX 1660 Ti'),
            ('NVIDIA Corporation', 'NVIDIA GeForce RTX 2060'),
            ('NVIDIA Corporation', 'NVIDIA GeForce RTX 3060'),
            ('NVIDIA Corporation', 'NVIDIA GeForce RTX 3080'),
            ('NVIDIA Corporation', 'NVIDIA GeForce MX250'),
            ('NVIDIA Corporation', 'NVIDIA GeForce GT 1030'),
            ('NVIDIA Corporation', 'NVIDIA Quadro P2000'),
            ('NVIDIA Corporation', 'NVIDIA RTX A2000'),
            ('AMD', 'AMD Radeon RX 580'),
            ('AMD', 'AMD Radeon RX 5700 XT'),
            ('AMD', 'AMD Radeon RX 6600 XT'),
            ('AMD', 'AMD Radeon Pro 5500M'),
            ('AMD', 'AMD Radeon Vega 8'),
            ('AMD', 'AMD Radeon R9 M370X'),
            ('Apple Inc.', 'Apple M1'),
            ('Apple Inc.', 'Apple M2'),
            ('Apple Inc.', 'Apple M1 Pro'),
            ('Apple Inc.', 'Apple M1 Max'),
            ('Apple Inc.', 'Apple M2 Max'),
        ]
        
        vendor, renderer = random.choice(vendor_renderer_pairs)
        
        driver.execute_script(f"""
        Object.defineProperty(navigator, 'plugins', {{ get: () => [1,2,3] }});
        Object.defineProperty(navigator, 'languages', {{ get: () => ['en-US', 'en'] }});
        const getParameter = WebGLRenderingContext.prototype.getParameter;
        WebGLRenderingContext.prototype.getParameter = function(param) {{
            if (param === 37445) return '{vendor}';
            if (param === 37446) return '{renderer}';
            return getParameter.call(this, param);
        }};
        """)

class BrowserSessionManagerApp:
    """Main application for Browser Session Manager."""
    def __init__(self):
        """Initialize the application."""
        self.db_manager = DatabaseManager()
        self.api_manager = APIManager()
        self.browser_manager = BrowserManager(self.db_manager)
        
        self.profiles_list = []
        self.current_index = -1
        self.current_driver = None
        self.is_running = False
        
        self._build_ui()
        
    def _build_ui(self):
        """Build the user interface."""
        # Set appearance mode and default color theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Create the main window
        self.root = ctk.CTk()
        self.root.title(f"Browser Session Manager v{APP_VERSION}")
        self.root.geometry("900x800")  # Increased window size
        self.root.minsize(800, 700)    # Set minimum window size
        self.root.configure(fg_color="#2b2b2b")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Create main frame
        self.main_frame = ctk.CTkFrame(self.root, fg_color="#2b2b2b")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            self.main_frame,
            text="Browser Session Manager",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#ffffff"
        )
        title_label.pack(pady=20)
        
        # API Credentials Frame
        credentials_frame = ctk.CTkFrame(self.main_frame, fg_color="#363636")
        credentials_frame.pack(fill="x", padx=10, pady=10)
        
        # API User ID
        self.api_user_id_var = tk.StringVar()
        ctk.CTkLabel(
            credentials_frame,
            text="API User ID:",
            font=ctk.CTkFont(size=12),
            text_color="#ffffff"
        ).pack(pady=(10, 0))
        ctk.CTkEntry(
            credentials_frame,
            textvariable=self.api_user_id_var,
            width=400,
            height=35,
            font=ctk.CTkFont(size=12)
        ).pack(pady=5)
        
        # API Key
        self.api_key_var = tk.StringVar()
        ctk.CTkLabel(
            credentials_frame,
            text="API Key:",
            font=ctk.CTkFont(size=12),
            text_color="#ffffff"
        ).pack(pady=(10, 0))
        ctk.CTkEntry(
            credentials_frame,
            textvariable=self.api_key_var,
            width=400,
            height=35,
            font=ctk.CTkFont(size=12),
            show="*"
        ).pack(pady=5)
        
        # File Selection Frame
        file_frame = ctk.CTkFrame(self.main_frame, fg_color="#363636")
        file_frame.pack(fill="x", padx=10, pady=10)
        
        self.file_path_var = tk.StringVar()
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
            textvariable=self.file_path_var,
            width=300,
            height=35,
            font=ctk.CTkFont(size=12)
        ).pack(side="left", padx=(0, 10))
        
        ctk.CTkButton(
            file_entry_frame,
            text="Browse",
            command=self.browse_file,
            width=100,
            height=35,
            font=ctk.CTkFont(size=12)
        ).pack(side="left")
        
        # Proxy Frame
        proxy_frame = ctk.CTkFrame(self.main_frame, fg_color="#363636")
        proxy_frame.pack(fill="x", padx=10, pady=10)
        
        self.proxy_var = tk.StringVar()
        ctk.CTkLabel(
            proxy_frame,
            text="Global Proxy (Optional):",
            font=ctk.CTkFont(size=12),
            text_color="#ffffff"
        ).pack(pady=(10, 0))
        ctk.CTkEntry(
            proxy_frame,
            textvariable=self.proxy_var,
            width=400,
            height=35,
            font=ctk.CTkFont(size=12),
            placeholder_text="Example: 123.456.789.012:8080 or user:pass@123.456.789.012:8080"
        ).pack(pady=5)
        
        # Buttons Frame
        buttons_frame = ctk.CTkFrame(self.main_frame, fg_color="#2b2b2b")
        buttons_frame.pack(fill="x", padx=10, pady=15)
        
        # Center container for buttons
        button_center_frame = ctk.CTkFrame(buttons_frame, fg_color="#2b2b2b")
        button_center_frame.pack()
        
        self.start_button = ctk.CTkButton(
            button_center_frame,
            text="Start Processing",
            command=self.run_process,
            width=200,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#28a745",
            hover_color="#218838"
        )
        self.start_button.pack(side="left", padx=5)
        
        self.next_button = ctk.CTkButton(
            button_center_frame,
            text="Skip to Next Profile",
            command=self.run_next_profile,
            width=200,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#007bff",
            hover_color="#0056b3"
        )
        self.next_button.pack(side="left", padx=5)
        
        # Progress Frame
        progress_frame = ctk.CTkFrame(self.main_frame, fg_color="#363636")
        progress_frame.pack(fill="x", padx=10, pady=10)
        
        self.progress_label = ctk.CTkLabel(
            progress_frame,
            text="Ready to process profiles",
            font=ctk.CTkFont(size=12),
            text_color="#ffffff"
        )
        self.progress_label.pack(pady=5)
        
        # Loading animation frame
        self.loading_frame = ctk.CTkFrame(progress_frame, fg_color="transparent")
        self.loading_frame.pack(pady=(0, 5))
        
        # Loading spinner label
        self.loading_label = ctk.CTkLabel(
            self.loading_frame,
            text="",
            font=ctk.CTkFont(size=16),
            text_color="#4CAF50"
        )
        self.loading_label.pack(pady=0)
        
        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(
            progress_frame,
            width=400,
            height=15,
            corner_radius=5,
            fg_color="#555555",
            progress_color="#4CAF50"
        )
        self.progress_bar.pack(pady=5)
        self.progress_bar.set(0)
        
        # Animation thread
        self.animation_running = False
        self.animation_thread = None
        
        # Console Frame
        console_frame = ctk.CTkFrame(self.main_frame, fg_color="#363636")
        console_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        console_label = ctk.CTkLabel(
            console_frame,
            text="Console Output:",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#ffffff"
        )
        console_label.pack(anchor="w", padx=10, pady=(10, 0))
        
        self.console = scrolledtext.ScrolledText(
            console_frame,
            wrap=tk.WORD,
            height=15,
            width=70,
            font=("Consolas", 10),
            bg="#1e1e1e",
            fg="#ffffff",
            insertbackground="#ffffff"
        )
        self.console.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Redirect stdout to console
        sys.stdout = TextLogger(self.console)
        
        # Version label
        version_label = ctk.CTkLabel(
            self.main_frame,
            text=f"Version {APP_VERSION}",
            font=ctk.CTkFont(size=10),
            text_color="#aaaaaa"
        )
        version_label.pack(pady=(0, 10))
        
        print(f"🚀 Browser Session Manager v{APP_VERSION} started.")
        print("Please select a CSV file with profiles and enter your API credentials.")
        
    def browse_file(self):
        """Open file dialog to select CSV file."""
        path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if path:
            self.file_path_var.set(path)
            print(f"📂 Selected file: {path}")
            
    def load_profiles(self, csv_path, override_proxy=None):
        """Load profiles from CSV file."""
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
            return True
        except Exception as e:
            print(f"❌ CSV Load Error: {e}")
            messagebox.showerror("Error", f"Failed to load CSV file: {e}")
            return False
            
    def run_process(self):
        """Start the profile processing."""
        # Get inputs
        csv_path = self.file_path_var.get().strip()
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
        
        # Load profiles
        if not self.load_profiles(csv_path, proxy_input):
            return
            
        # Reset index and start processing
        self.current_index = -1
        self.is_running = True
        self.progress_bar.set(0)
        
        # Start processing
        self.run_next_profile()
        
    def _start_loading_animation(self):
        """Start the animated loading indicator."""
        if self.animation_running:
            return
            
        def animate():
            # Animation characters - spinner
            frames = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
            
            # Alternative animation - dots
            # frames = ['⠋', '⠋⠙', '⠋⠙⠚', '⠋⠙⠚⠒', '⠋⠙⠚⠒⠂', '⠋⠙⠚⠒⠂⠁', '⠋⠙⠚⠒⠂', '⠋⠙⠚⠒', '⠋⠙⠚', '⠋⠙', '⠋']
            
            # Another alternative - block building
            # frames = ['▁', '▂', '▃', '▄', '▅', '▆', '▇', '█', '▇', '▆', '▅', '▄', '▃', '▂']
            
            i = 0
            while self.animation_running:
                frame = frames[i % len(frames)]
                
                # Update the loading label text safely using the main thread
                self.root.after(0, lambda f=frame: self.loading_label.configure(text=f" {f} Loading browser..."))
                
                time.sleep(0.1)
                i += 1

        self.animation_running = True
        self.animation_thread = threading.Thread(target=animate)
        self.animation_thread.daemon = True
        self.animation_thread.start()
        
    def _stop_loading_animation(self):
        """Stop the animated loading indicator."""
        self.animation_running = False
        if self.animation_thread:
            # Wait for animation thread to finish
            if self.animation_thread.is_alive():
                self.animation_thread.join(timeout=0.5)
            self.animation_thread = None
            
        # Clear the loading label
        self.loading_label.configure(text="")
            
    def run_next_profile(self):
        """Process the next profile in the list."""
        # Stop any running animations first
        self._stop_loading_animation()
        
        # Close current browser if open
        if self.current_driver:
            try:
                print("💾 Saving current session...")
                cookies = self.current_driver.get_cookies()
                user_agent = self.current_driver.execute_script("return navigator.userAgent")
                profile_id, _ = self.profiles_list[self.current_index]
                self.db_manager.save_session(profile_id, user_agent, cookies)
                
                # Close browser
                print("🔚 Closing browser...")
                self.current_driver.quit()
            except Exception as e:
                print(f"⚠️ Warning: {e}")
            finally:
                self.current_driver = None
                # Ensure Chrome processes are killed
                self.browser_manager.kill_chrome_processes()
                
        # Move to next profile
        self.current_index += 1
        
        # Check if there are more profiles to process
        if self.current_index < len(self.profiles_list):
            profile_id, proxy = self.profiles_list[self.current_index]
            
            # Update progress
            progress_value = (self.current_index) / len(self.profiles_list) if self.profiles_list else 0
            self.progress_bar.set(progress_value)
            self.progress_label.configure(text=f"Processing profile {self.current_index + 1}/{len(self.profiles_list)}: {profile_id}")
            
            print(f"\n🚀 Starting profile {self.current_index + 1}/{len(self.profiles_list)}: {profile_id}")
            print(f"🌐 Proxy: {proxy or 'None'}")
            
            # Start the loading animation
            self._start_loading_animation()
            
            # Set a maximum number of retries
            max_retries = 2
            for retry in range(max_retries + 1):
                try:
                    print(f"🔄 Launching browser (attempt {retry + 1}/{max_retries + 1})...")
                    self.current_driver, _ = self.browser_manager.launch_browser(profile_id, proxy)
                    # If we get here, browser was launched successfully
                    # Stop the loading animation
                    self._stop_loading_animation()
                    # Set success message
                    self.loading_label.configure(text=" ✅ Browser ready", text_color="#4CAF50")
                    break
                except Exception as e:
                    print(f"❌ Error launching browser for {profile_id}: {e}")
                    print(f"Traceback: {traceback.format_exc()}")
                    if retry < max_retries:
                        print(f"⏱️ Retrying in 3 seconds...")
                        time.sleep(3)
                    else:
                        # Stop the loading animation
                        self._stop_loading_animation()
                        # Set error message
                        self.loading_label.configure(text=" ❌ Browser launch failed", text_color="#FF5252")
                        print(f"⚠️ Failed to launch browser after {max_retries + 1} attempts. Skipping profile.")
                        # Proceed to next profile
                        self.root.after(1000, self.run_next_profile)
                        return
        else:
            # All profiles processed
            self.is_running = False
            self.progress_bar.set(1)
            self.progress_label.configure(text="All profiles processed")
            # Make sure animation is stopped
            self._stop_loading_animation()
            # Set completed message
            self.loading_label.configure(text=" ✅ All profiles completed", text_color="#4CAF50")
            print("✅ All profiles processed.")
            print("🎉 Browser Session Manager has completed processing all profiles.")
            messagebox.showinfo("Complete", "All profiles have been processed.")
            
    def on_close(self):
        """Handle window close event."""
        # Stop any running animations
        self._stop_loading_animation()
        
        # Close browser if open
        if self.current_driver:
            try:
                self.current_driver.quit()
            except:
                pass
                
        # Kill any remaining Chrome processes
        self.browser_manager.kill_chrome_processes()
        
        # Restore stdout and destroy the window
        sys.stdout = sys.__stdout__
        self.root.destroy()
        
    def run(self):
        """Run the application."""
        self.root.mainloop()

def create_sample_csv():
    """Create a sample CSV file for profiles."""
    if not os.path.exists('sample_profiles.csv'):
        with open('sample_profiles.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['profile_id', 'proxy'])
            writer.writerow(['profile1', ''])
            writer.writerow(['profile2', '123.456.789.012:8080'])
            writer.writerow(['profile3', 'user:pass@123.456.789.012:8080'])
            writer.writerow(['gmail_account1', ''])
            writer.writerow(['gmail_account2', ''])
            writer.writerow(['work_profile', ''])
        print("✅ Created sample_profiles.csv")

def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(description='Browser Session Manager')
    parser.add_argument('--create-sample', action='store_true', help='Create a sample profiles CSV file')
    args = parser.parse_args()
    
    # Create sample CSV file if requested
    if args.create_sample:
        create_sample_csv()
        return
        
    # Make sure the browser profiles directory exists
    os.makedirs(BROWSER_PROFILES_DIR, exist_ok=True)
    
    # Start the application
    app = BrowserSessionManagerApp()
    app.run()

if __name__ == "__main__":
    main()