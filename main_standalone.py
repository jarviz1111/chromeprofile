"""
Browser Session Manager
-----------------------
A GUI application for managing browser sessions, profiles, and automating browser interactions.
"""
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import csv
import os
import threading
import requests
import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent
import sqlite3
import json
import time
import random
from datetime import datetime
import sys
import psutil
import customtkinter as ctk

DB_PATH = 'browser_sessions.db'
LOGIN_URL = "https://accounts.google.com/signup"

current_driver = None
profiles_list = []
current_index = -1

class TextLogger:
    def __init__(self, textbox):
        self.textbox = textbox

    def write(self, msg):
        if self.textbox:
            # Enable the text widget temporarily to insert text
            self.textbox.config(state=tk.NORMAL)
            self.textbox.insert(tk.END, msg)
            self.textbox.see(tk.END)
            # Disable it again to make it read-only
            self.textbox.config(state=tk.DISABLED)
        sys.__stdout__.write(msg)

    def flush(self):
        pass

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS sessions (
            profile TEXT PRIMARY KEY,
            user_agent TEXT,
            cookies TEXT
        )''')
        c.execute("PRAGMA table_info(sessions)")
        columns = [col[1] for col in c.fetchall()]
        if 'updated_at' not in columns:
            c.execute("ALTER TABLE sessions ADD COLUMN updated_at TEXT")
        conn.commit()

def save_session(profile, user_agent, cookies):
    try:
        with sqlite3.connect(DB_PATH, timeout=10) as conn:
            c = conn.cursor()
            now = datetime.utcnow().isoformat()
            c.execute('''INSERT OR REPLACE INTO sessions 
                         (profile, user_agent, cookies, updated_at)
                         VALUES (?, ?, ?, ?)''',
                      (profile, user_agent, json.dumps(cookies), now))
            conn.commit()
        return True
    except Exception as e:
        print(f"❌ DB Save Error: {e}")
        return False

def load_session(profile):
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('SELECT user_agent, cookies FROM sessions WHERE profile = ?', (profile,))
        result = c.fetchone()
        if result:
            return result[0], json.loads(result[1]) if result[1] else None
        return None, None

def verify_api(api_user_id, api_key_id):
    """
    Verify API credentials. This is a placeholder that can be replaced with your actual API verification.
    
    For testing purposes, the function will return True for any non-empty credentials.
    In a production environment, this should be replaced with actual API verification.
    """
    try:
        # For demonstration purposes only - in a real app this would contact the actual API
        if api_user_id and api_key_id:
            # Uncomment the following in production
            # api_link = f"https://inboxinnovations.org?menuname=seeding&userid={api_user_id}&keyid={api_key_id}"
            # response = requests.get(api_link, timeout=10)
            # return response.text.strip() == "1"
            
            # For demonstration, always return True for non-empty credentials
            print("✅ API credentials accepted (DEMO MODE)")
            return True
        else:
            print("❌ API credentials cannot be empty")
            return False
    except Exception as e:
        print(f"❌ API verification failed: {e}")
        return False

def kill_chrome():
    for proc in psutil.process_iter():
        try:
            if proc.name().lower() in ["chrome.exe", "chromedriver.exe", "chrome", "chromedriver"]:
                proc.kill()
        except:
            pass

def launch_browser_return_driver(profile_id, proxy=None):
    print(f"🟢 Launching browser for profile: {profile_id}")
    user_data_dir = os.path.join("browser_profiles", profile_id)
    os.makedirs(user_data_dir, exist_ok=True)
    
    stored_user_agent, stored_cookies = load_session(profile_id)

    if stored_user_agent:
        user_agent = stored_user_agent
    else:
        try:
            ua = UserAgent()
            for _ in range(10):
                candidate = ua.chrome
                if all(x not in candidate.lower() for x in ['mobile', 'android', 'iphone', 'ipad']):
                    user_agent = candidate
                    break
            else:
                user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        except Exception as e:
            print(f"⚠️ Error loading fake_useragent: {e}")
            user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"

    options = uc.ChromeOptions()
    options.add_argument(f"--user-agent={user_agent}")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-extensions")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument(f"--user-data-dir={user_data_dir}")

    if proxy:
        options.add_argument(f"--proxy-server=http://{proxy}")
        print(f"🌐 Using Proxy: {proxy}")
    else:
        print("🚫 No proxy set.")

    driver = uc.Chrome(options=options)

    driver.execute_cdp_cmd('Network.setUserAgentOverride', {
        "userAgent": user_agent,
        "acceptLanguage": "en-US,en;q=0.9",
        "platform": "Win32"
    })
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

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

    if stored_cookies:
        print("🟡 Loading cookies...")
        driver.get("https://accounts.google.com/")
        for cookie in stored_cookies:
            if 'sameSite' in cookie:
                del cookie['sameSite']
            try:
                driver.add_cookie(cookie)
            except:
                pass
        driver.get("https://mail.google.com/")
    else:
        print("🟢 No cookies found. Creating new session...")
        driver.get(LOGIN_URL)
        print("⚠️  Please login manually...")
        time.sleep(30)
        cookies = driver.get_cookies()
        save_session(profile_id, user_agent, cookies)

    return driver

def load_profiles(csv_path, override_proxy):
    global profiles_list
    profiles_list = []
    try:
        with open(csv_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                profile_id = row.get('profile_id', '').strip()
                if not profile_id:
                    continue
                proxy = override_proxy if override_proxy else (row.get('proxy', '') or '').strip()
                proxy = proxy if proxy else None
                profiles_list.append((profile_id, proxy))
        
        print(f"✅ Loaded {len(profiles_list)} profiles from CSV.")
    except Exception as e:
        print(f"❌ CSV Load Error: {e}")

def rename_profile(old_profile_name, new_profile_name):
    """Rename a profile in the database.
    
    Args:
        old_profile_name (str): Current profile name
        new_profile_name (str): New profile name
        
    Returns:
        bool: True if rename was successful, False otherwise
    """
    try:
        # First check if the old profile exists
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute('SELECT * FROM sessions WHERE profile = ?', (old_profile_name,))
            old_profile_data = c.fetchone()
            
            if not old_profile_data:
                print(f"❌ Profile not found: {old_profile_name}")
                return False
                
            # Check if the new name already exists
            c.execute('SELECT * FROM sessions WHERE profile = ?', (new_profile_name,))
            if c.fetchone():
                print(f"❌ Cannot rename: Profile '{new_profile_name}' already exists")
                return False
                
            # Update the profile name
            c.execute('UPDATE sessions SET profile = ? WHERE profile = ?', 
                      (new_profile_name, old_profile_name))
            conn.commit()
            
            print(f"✅ Profile renamed from '{old_profile_name}' to '{new_profile_name}'")
            return True
            
    except Exception as e:
        print(f"❌ DB Rename Error: {e}")
        return False

def get_all_profiles():
    """Get all profiles from the database."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute('SELECT profile, updated_at FROM sessions ORDER BY updated_at DESC')
            return c.fetchall()
    except Exception as e:
        print(f"❌ DB Load Error: {e}")
        return []

def show_profiles_window():
    """Show a window with all saved profiles and options to edit them."""
    # Get all profiles from the database
    stored_profiles = get_all_profiles()
    
    if not stored_profiles:
        messagebox.showinfo("No Profiles", "No saved profiles found in the database.")
        return
        
    # Create a new top-level window
    profiles_window = ctk.CTkToplevel()
    profiles_window.title("Saved Browser Profiles")
    profiles_window.geometry("800x600")
    profiles_window.grab_set()  # Make window modal
    
    # Create a frame for the profiles list
    list_frame = ctk.CTkFrame(profiles_window, fg_color="#2b2b2b")
    list_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    # Title
    ctk.CTkLabel(
        list_frame,
        text="Saved Browser Profiles",
        font=ctk.CTkFont(size=20, weight="bold"),
        text_color="#ffffff"
    ).pack(pady=(0, 20))
    
    # Instructions
    ctk.CTkLabel(
        list_frame,
        text="Double-click on a profile to edit its name",
        font=ctk.CTkFont(size=12),
        text_color="#aaaaaa"
    ).pack(pady=(0, 10))
    
    # Create frame for the table
    table_frame = ctk.CTkFrame(list_frame, fg_color="#363636")
    table_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Create a listbox with scrollbar for profiles
    list_container = ctk.CTkFrame(table_frame, fg_color="transparent")
    list_container.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Listbox with custom styling
    listbox = tk.Listbox(
        list_container,
        font=("Consolas", 12),
        bg="#1e1e1e",
        fg="#ffffff",
        selectbackground="#28a745",
        selectforeground="#ffffff",
        width=50,
        height=20,
        exportselection=0,
        activestyle="none"
    )
    listbox.pack(side="left", fill="both", expand=True)
    
    # Scrollbar
    scrollbar = tk.Scrollbar(list_container)
    scrollbar.pack(side="right", fill="y")
    
    # Connect listbox and scrollbar
    listbox.config(yscrollcommand=scrollbar.set)
    scrollbar.config(command=listbox.yview)
    
    # Populate the listbox with profiles
    for i, (profile_id, updated_at) in enumerate(stored_profiles):
        # Format the date if it exists
        if updated_at:
            try:
                dt = datetime.fromisoformat(updated_at)
                formatted_date = dt.strftime("%Y-%m-%d %H:%M:%S")
            except:
                formatted_date = updated_at
        else:
            formatted_date = "Unknown"
            
        listbox.insert(tk.END, f"{profile_id} (Last updated: {formatted_date})")
    
    # Dictionary to store edited profile names
    edited_profiles = {}
    
    # Edit profile frame (initially hidden)
    edit_frame = ctk.CTkFrame(list_frame, fg_color="#363636")
    
    # Widgets for edit frame
    profile_var = tk.StringVar()
    original_profile_var = tk.StringVar()
    
    ctk.CTkLabel(
        edit_frame,
        text="Edit Profile Name:",
        font=ctk.CTkFont(size=14),
        text_color="#ffffff"
    ).pack(pady=(10, 5))
    
    edit_entry = ctk.CTkEntry(
        edit_frame,
        textvariable=profile_var,
        width=300,
        height=35,
        font=ctk.CTkFont(size=14)
    )
    edit_entry.pack(pady=5)
    
    buttons_frame = ctk.CTkFrame(edit_frame, fg_color="transparent")
    buttons_frame.pack(pady=10)
    
    def save_edited_profile():
        original = original_profile_var.get()
        new_name = profile_var.get().strip()
        
        if not new_name:
            messagebox.showerror("Error", "Profile name cannot be empty.")
            return
            
        if original != new_name:
            # Store the edited name
            edited_profiles[original] = new_name
            
            # Update the listbox
            selected_index = listbox.curselection()[0]
            current_text = listbox.get(selected_index)
            date_part = current_text.split("(Last updated:")[1].strip()
            new_text = f"{new_name} (Last updated: {date_part}"
            listbox.delete(selected_index)
            listbox.insert(selected_index, new_text)
            
            # Hide edit frame and show success message
            edit_frame.pack_forget()
            messagebox.showinfo("Success", f"Profile name changed from '{original}' to '{new_name}'.\n\nChanges will be saved when you close this window.")
    
    def cancel_edit():
        edit_frame.pack_forget()
    
    # Save and Cancel buttons
    ctk.CTkButton(
        buttons_frame,
        text="Save Changes",
        command=save_edited_profile,
        width=150,
        height=35,
        font=ctk.CTkFont(size=12),
        fg_color="#28a745",
        hover_color="#218838"
    ).pack(side="left", padx=5)
    
    ctk.CTkButton(
        buttons_frame,
        text="Cancel",
        command=cancel_edit,
        width=150,
        height=35,
        font=ctk.CTkFont(size=12),
        fg_color="#dc3545",
        hover_color="#c82333"
    ).pack(side="left", padx=5)
    
    # Handle double click on a profile
    def on_profile_double_click(event):
        try:
            # Get the selected item
            selection = listbox.curselection()[0]
            value = listbox.get(selection)
            profile_id = value.split(" (Last updated:")[0]
            
            # Set up editing
            original_profile_var.set(profile_id)
            profile_var.set(profile_id)
            
            # Show edit frame
            edit_frame.pack(fill="x", padx=10, pady=10)
            edit_entry.focus_set()
        except (IndexError, Exception) as e:
            print(f"Error selecting profile: {e}")
    
    # Bind double click event
    listbox.bind("<Double-1>", on_profile_double_click)
    
    # Button frame at the bottom
    bottom_frame = ctk.CTkFrame(list_frame, fg_color="transparent")
    bottom_frame.pack(fill="x", pady=10)
    
    def close_and_save():
        # Save all edited profiles
        if edited_profiles:
            for original, new_name in edited_profiles.items():
                try:
                    success = rename_profile(original, new_name)
                    if success:
                        print(f"✅ Profile renamed: {original} → {new_name}")
                    else:
                        print(f"❌ Failed to rename profile: {original}")
                except Exception as e:
                    print(f"❌ Error renaming profile {original}: {e}")
            
            # Let the user know
            print(f"✅ Saved {len(edited_profiles)} renamed profiles.")
            
        # Close the window
        profiles_window.destroy()
    
    # Close button
    ctk.CTkButton(
        bottom_frame,
        text="Close",
        command=close_and_save,
        width=200,
        height=40,
        font=ctk.CTkFont(size=14),
        fg_color="#007bff",
        hover_color="#0056b3"
    ).pack(pady=10)

def _close_browser_thread():
    """Close browser in background thread to prevent UI from freezing."""
    global current_driver
    
    # Save current session before closing if we have an active driver
    if current_driver:
        try:
            profile_id, _ = profiles_list[current_index]
            print(f"💾 Saving session for {profile_id}...")
            
            try:
                # Get cookies and user agent
                cookies = current_driver.get_cookies()
                user_agent = current_driver.execute_script("return navigator.userAgent")
                
                # Save to database
                if save_session(profile_id, user_agent, cookies):
                    print(f"✅ Session saved for profile: {profile_id}")
                else:
                    print(f"⚠️ Warning: Could not save session for {profile_id}")
            except Exception as save_error:
                print(f"⚠️ Session save error: {save_error}")
                
            # Close browser
            print("🔚 Closing browser...")
            try:
                current_driver.quit()
            except Exception as quit_error:
                print(f"⚠️ Browser quit error: {quit_error}")
                
        except Exception as e:
            print(f"⚠️ Browser close warning: {e}")
        finally:
            # Ensure Chrome processes are killed
            try:
                kill_chrome()
            except Exception as kill_error:
                print(f"⚠️ Chrome kill error: {kill_error}")
    
    # Schedule UI updates from the main thread
    root.after(100, _finalize_browser_close)
    
def _finalize_browser_close():
    """Final steps after browser close, runs in main thread."""
    global current_driver
    
    # Reset current driver
    current_driver = None
    # Stop loading animation if active
    _stop_loading_animation()
    
    # Proceed to next profile
    _proceed_to_next_profile()
    
def _proceed_to_next_profile():
    """Proceed to the next profile after cleanup is complete."""
    global current_index
    
    # Move to next profile
    current_index += 1
    
    # Check if there are more profiles to process
    if current_index < len(profiles_list):
        # Start loading animation for next profile
        _start_loading_animation()
        
        # Start processing in a background thread
        threading.Thread(target=_process_profile_thread, daemon=True).start()
    else:
        print("✅ All profiles processed.")
        print("🎉 Browser Session Manager has completed processing all profiles.")

def _process_profile_thread():
    """Process the current profile in a background thread."""
    global current_driver
    
    try:
        profile_id, proxy = profiles_list[current_index]
        print(f"\n🚀 Starting profile {current_index + 1}/{len(profiles_list)}: {profile_id}")
        print(f"🌐 Proxy: {proxy or 'None'}")
        
        # Set a maximum number of retries
        max_retries = 2
        success = False
        
        for retry in range(max_retries + 1):
            try:
                print(f"🔄 Launching browser (attempt {retry + 1}/{max_retries + 1})...")
                current_driver = launch_browser_return_driver(profile_id, proxy)
                # If we get here, browser was launched successfully
                success = True
                break
            except Exception as e:
                print(f"❌ Error launching browser for {profile_id}: {e}")
                if retry < max_retries:
                    print(f"⏱️ Retrying in 3 seconds...")
                    time.sleep(3)
                else:
                    print(f"⚠️ Failed to launch browser after {max_retries + 1} attempts. Skipping profile.")
        
        # If we could not launch the browser successfully, move to next profile
        if not success:
            root.after(0, _finalize_browser_close)
            return
            
        # Start browser monitoring
        root.after(1000, _check_for_dead_browser)
        
        # Stop loading animation
        root.after(0, _stop_loading_animation)
        
    except Exception as e:
        print(f"❌ Error in profile processing: {e}")
        root.after(0, _stop_loading_animation)

def run_next_profile():
    """User-initiated function to move to the next profile."""
    # Start loading animation
    _start_loading_animation()
    
    # Close current browser in background thread if it exists
    if current_driver:
        threading.Thread(target=_close_browser_thread, daemon=True).start()
    else:
        # If no browser is running, proceed directly to next profile
        _proceed_to_next_profile()

def start_gui():
    def browse_file():
        path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if path:
            file_path_var.set(path)

    # Loading animation variables
    loading_animation = None
    loading_active = False
    loading_label = None
    animation_style = "spinner"  # options: "spinner", "dots", "blocks"
    
    def _start_loading_animation():
        nonlocal loading_animation, loading_active, loading_label
        
        # Create a label for the animation if it doesn't exist
        if loading_label is None:
            loading_label = ctk.CTkLabel(
                main_frame,
                text="",
                font=ctk.CTkFont(size=16),
                text_color="#ffcc00"
            )
            loading_label.pack(pady=(5, 10))
            
        loading_active = True
        
        # Different animation styles
        def animate():
            if not loading_active:
                loading_label.configure(text="")
                return
                
            if animation_style == "spinner":
                frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
                current_frame = int(time.time() * 10) % len(frames)
                loading_label.configure(text=f"{frames[current_frame]} Loading browser session... Please wait")
            elif animation_style == "dots":
                frames = [".", "..", "...", "...."]
                current_frame = int(time.time() * 2) % len(frames)
                loading_label.configure(text=f"Loading browser session{frames[current_frame]}")
            elif animation_style == "blocks":
                frames = ["▰▱▱▱▱▱▱▱", "▰▰▱▱▱▱▱▱", "▰▰▰▱▱▱▱▱", "▰▰▰▰▱▱▱▱", 
                         "▰▰▰▰▰▱▱▱", "▰▰▰▰▰▰▱▱", "▰▰▰▰▰▰▰▱", "▰▰▰▰▰▰▰▰"]
                current_frame = int(time.time() * 3) % len(frames)
                loading_label.configure(text=f"Loading: {frames[current_frame]}")
            
            # Schedule the next animation frame
            loading_animation = root.after(100, animate)
            
        # Start the animation
        animate()
    
    def _stop_loading_animation():
        nonlocal loading_animation, loading_active
        loading_active = False
        if loading_animation:
            root.after_cancel(loading_animation)
            loading_animation = None
        if loading_label:
            loading_label.configure(text="")
            
    def _check_for_dead_browser():
        """Monitor if browser is still alive, handle it if manually closed."""
        global current_driver
        
        # If we have no browser instance, nothing to check
        if current_driver is None:
            return
            
        try:
            # Try to get a simple property to check if browser is still accessible
            current_driver.current_url
            # If we get here, browser is still alive, schedule another check
            root.after(2000, _check_for_dead_browser)
        except Exception:
            # Browser is no longer accessible, likely manually closed
            print("⚠️ Browser appears to have been closed manually.")
            _handle_closed_browser()
            
    def _handle_closed_browser():
        """Handle browser that was closed manually."""
        # Run cleanup in a background thread to prevent UI from freezing
        threading.Thread(target=_cleanup_browser_thread, daemon=True).start()
    
    def _cleanup_browser_thread():
        """Clean up browser in background thread to prevent UI from freezing."""
        global current_driver
        
        try:
            # Kill any remaining chrome processes
            kill_chrome()
            print("✅ Chrome processes cleaned up after manual browser closure.")
        except Exception as e:
            print(f"⚠️ Error during browser cleanup: {e}")
        finally:
            # Schedule UI updates from the main thread
            root.after(100, _finalize_browser_cleanup)
            
    def _finalize_browser_cleanup():
        """Final steps after browser cleanup, runs in main thread."""
        global current_driver
        
        # Reset current driver
        current_driver = None
        # Stop loading animation if active
        _stop_loading_animation()
        print("🔄 Ready for the next operation.")
            
    def _process_next_profile_thread():
        """Process the next profile in a background thread."""
        try:
            # Start browser monitoring
            root.after(2000, _check_for_dead_browser)
            
            # Call the actual profile processing function
            run_next_profile()
        except Exception as e:
            print(f"❌ Error in profile processing: {e}")
        finally:
            # Always stop the loading animation when done
            root.after(0, _stop_loading_animation)
    
    def run_process():
        csv_path = file_path_var.get()
        proxy_input = proxy_var.get().strip()
        api_user_id = api_user_id_var.get().strip()
        api_key_id = api_key_var.get().strip()

        if not os.path.exists(csv_path):
            messagebox.showerror("Error", "CSV file not found.")
            return

        if not api_user_id or not api_key_id:
            messagebox.showerror("Error", "API credentials are required.")
            return

        print("🔑 Verifying API credentials...")
        if not verify_api(api_user_id, api_key_id):
            messagebox.showerror("Access Denied", "Invalid API credentials.")
            return
        
        print("✅ API credentials verified.")

        init_db()
        load_profiles(csv_path, proxy_input)
        
        # Reset current index
        global current_index
        current_index = -1
        
        # Start loading animation
        _start_loading_animation()
        
        # Start processing in a background thread
        threading.Thread(target=_process_next_profile_thread, daemon=True).start()

    def on_closing():
        global current_driver
        if current_driver:
            try:
                current_driver.quit()
            except:
                pass
        kill_chrome()
        sys.stdout = sys.__stdout__
        root.destroy()

    # Set appearance mode and default color theme
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    # Create the main window
    root = ctk.CTk()
    root.title("Browser Session Manager")
    root.geometry("1000x900")  # Increased window size for bigger console
    root.minsize(900, 800)    # Set minimum window size
    root.configure(fg_color="#2b2b2b")
    root.protocol("WM_DELETE_WINDOW", on_closing)

    # Create main frame
    main_frame = ctk.CTkFrame(root, fg_color="#2b2b2b")
    main_frame.pack(fill="both", expand=True, padx=20, pady=20)

    # Title
    title_label = ctk.CTkLabel(
        main_frame,
        text="Browser Session Manager",
        font=ctk.CTkFont(size=24, weight="bold"),
        text_color="#ffffff"
    )
    title_label.pack(pady=20)

    # API Credentials Frame
    credentials_frame = ctk.CTkFrame(main_frame, fg_color="#363636")
    credentials_frame.pack(fill="x", padx=10, pady=10)

    # API User ID
    api_user_id_var = tk.StringVar()
    ctk.CTkLabel(
        credentials_frame,
        text="API User ID:",
        font=ctk.CTkFont(size=12),
        text_color="#ffffff"
    ).pack(pady=(10, 0))
    ctk.CTkEntry(
        credentials_frame,
        textvariable=api_user_id_var,
        width=400,
        height=35,
        font=ctk.CTkFont(size=12)
    ).pack(pady=5)

    # API Key
    api_key_var = tk.StringVar()
    ctk.CTkLabel(
        credentials_frame,
        text="API Key:",
        font=ctk.CTkFont(size=12),
        text_color="#ffffff"
    ).pack(pady=(10, 0))
    ctk.CTkEntry(
        credentials_frame,
        textvariable=api_key_var,
        width=400,
        height=35,
        font=ctk.CTkFont(size=12),
        show="*"
    ).pack(pady=5)

    # File Selection Frame
    file_frame = ctk.CTkFrame(main_frame, fg_color="#363636")
    file_frame.pack(fill="x", padx=10, pady=10)

    file_path_var = tk.StringVar()
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
        command=browse_file,
        width=100,
        height=35,
        font=ctk.CTkFont(size=12)
    ).pack(side="left")

    # Proxy Frame
    proxy_frame = ctk.CTkFrame(main_frame, fg_color="#363636")
    proxy_frame.pack(fill="x", padx=10, pady=10)

    proxy_var = tk.StringVar()
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

    # Buttons Frame - Changed to center align buttons with better spacing
    buttons_frame = ctk.CTkFrame(main_frame, fg_color="#2b2b2b")
    buttons_frame.pack(fill="x", padx=10, pady=15)
    
    # Center container for buttons
    button_center_frame = ctk.CTkFrame(buttons_frame, fg_color="#2b2b2b")
    button_center_frame.pack(pady=10)
    
    # Information about DEMO mode
    demo_label = ctk.CTkLabel(
        buttons_frame,
        text="DEMO MODE: Any non-empty API credentials will be accepted",
        font=ctk.CTkFont(size=12, slant="italic"),
        text_color="#ffcc00"
    )
    demo_label.pack(pady=(0, 5))
    
    # Start Button with much improved visibility
    start_button = ctk.CTkButton(
        button_center_frame,
        text="START PROCESSING",
        command=lambda: threading.Thread(target=run_process).start(),
        width=180,
        height=50,
        font=ctk.CTkFont(size=14, weight="bold"),
        fg_color="#28a745",
        hover_color="#218838",
        border_width=2,
        border_color="#1e7e34",
        corner_radius=10
    )
    start_button.pack(side="left", padx=5, pady=10)

    # Next Profile Button with much improved visibility
    next_button = ctk.CTkButton(
        button_center_frame,
        text="NEXT PROFILE ▶",
        command=lambda: threading.Thread(target=run_next_profile).start(),
        width=180,
        height=50,
        font=ctk.CTkFont(size=14, weight="bold"),
        fg_color="#007bff",
        hover_color="#0056b3",
        border_width=2,
        border_color="#0062cc",
        corner_radius=10
    )
    next_button.pack(side="left", padx=5, pady=10)
    
    # List/Edit Profiles Button
    list_profiles_button = ctk.CTkButton(
        button_center_frame,
        text="LIST/EDIT PROFILES",
        command=lambda: threading.Thread(target=show_profiles_window).start(),
        width=180,
        height=50,
        font=ctk.CTkFont(size=14, weight="bold"),
        fg_color="#9933CC",
        hover_color="#7722AA",
        border_width=2,
        border_color="#8822BB",
        corner_radius=10
    )
    list_profiles_button.pack(side="left", padx=5, pady=10)

    # Console Frame
    console_frame = ctk.CTkFrame(main_frame, fg_color="#363636")
    console_frame.pack(fill="both", expand=True, padx=10, pady=10)

    ctk.CTkLabel(
        console_frame,
        text="Process Log:",
        font=ctk.CTkFont(size=12),
        text_color="#ffffff"
    ).pack(anchor="w", padx=10, pady=(10, 0))

    console = scrolledtext.ScrolledText(
        console_frame,
        wrap=tk.WORD,
        height=25,  # Increased from 15 to 25 to show more lines
        width=80,   # Increased width from 70 to 80
        font=("Consolas", 11),  # Slightly larger font
        bg="#1e1e1e",
        fg="#ffffff",
        insertbackground="#ffffff",
        state=tk.DISABLED  # Make it read-only to prevent UI freezing when clicking
    )
    console.pack(fill="both", expand=True, padx=10, pady=10)
    sys.stdout = TextLogger(console)
    
    print("🚀 Browser Session Manager started.")
    print("Please select a CSV file with profiles and enter your API credentials.")

    root.mainloop()

if __name__ == "__main__":
    start_gui()