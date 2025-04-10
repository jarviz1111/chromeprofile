"""
Browser Driver Module
---------------------
Handles browser initialization, configuration, and automation.
"""
import os
import random
import time
import json
from pathlib import Path
from fake_useragent import UserAgent
import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException

class BrowserDriver:
    """Handles browser initialization and automation using undetected_chromedriver."""
    
    def __init__(self, session_manager, temp_dir="browser_profiles"):
        """Initialize the browser driver with session manager.
        
        Args:
            session_manager: Instance of SessionManager for cookie/session handling.
            temp_dir (str): Directory for storing browser profiles.
        """
        self.session_manager = session_manager
        self.temp_dir = temp_dir
        self.driver = None
        self.current_profile = None
        
        # Create temp directory if it doesn't exist
        os.makedirs(self.temp_dir, exist_ok=True)
    
    def generate_user_agent(self):
        """Generate a desktop user agent string.
        
        Returns:
            str: A user agent string for desktop browsers.
        """
        try:
            ua = UserAgent()
            for _ in range(10):
                candidate = ua.chrome
                if all(x not in candidate.lower() for x in ['mobile', 'android', 'iphone', 'ipad']):
                    return candidate
            # Fallback user agent
            return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        except Exception as e:
            print(f"⚠️ Error loading fake_useragent: {e}")
            return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    
    def close(self):
        """Close the current browser session if open."""
        if self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                print(f"⚠️ Error closing browser: {e}")
            finally:
                self.driver = None
                self.current_profile = None
    
    def launch(self, profile_id, proxy=None, login_url="https://accounts.google.com/signup"):
        """Launch a browser session with the specified profile.
        
        Args:
            profile_id (str): Profile identifier.
            proxy (str, optional): Proxy to use in format "ip:port" or "user:pass@ip:port".
            login_url (str): URL to navigate to for login if no session exists.
            
        Returns:
            bool: True if launch was successful, False otherwise.
        """
        self.close()  # Close any existing session
        
        print(f"🟢 Launching browser for profile: {profile_id}")
        self.current_profile = profile_id
        user_data_dir = os.path.join(self.temp_dir, profile_id)
        
        # Load existing session if available
        stored_user_agent, stored_cookies = self.session_manager.load_session(profile_id)
        
        user_agent = stored_user_agent if stored_user_agent else self.generate_user_agent()
        
        try:
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
            
            if proxy:
                options.add_argument(f"--proxy-server=http://{proxy}")
                print(f"🌐 Using Proxy: {proxy}")
            else:
                print("🚫 No proxy set.")
            
            # Launch undetected Chrome
            self.driver = uc.Chrome(options=options)
            
            # Apply anti-fingerprinting measures
            self._apply_fingerprinting_protections(user_agent)
            
            if stored_cookies:
                print("🟡 Loading cookies...")
                self.driver.get("https://accounts.google.com/")
                for cookie in stored_cookies:
                    if 'sameSite' in cookie:
                        del cookie['sameSite']
                    try:
                        self.driver.add_cookie(cookie)
                    except:
                        pass
                self.driver.get("https://mail.google.com/")
            else:
                print("🟢 No cookies found. Creating new session...")
                self.driver.get(login_url)
                print("⚠️ Please login manually...")
                time.sleep(10)  # Give a moment for the login page to load
            
            return True
        except Exception as e:
            print(f"❌ Error launching browser: {e}")
            self.close()
            return False
    
    def save_current_session(self):
        """Save the current browser session to the database."""
        if not self.driver or not self.current_profile:
            print("❌ No active browser session to save.")
            return False
        
        try:
            cookies = self.driver.get_cookies()
            user_agent = self.driver.execute_script("return navigator.userAgent")
            
            success = self.session_manager.save_session(
                self.current_profile, 
                user_agent, 
                cookies
            )
            
            if success:
                print(f"✅ Session saved for profile: {self.current_profile}")
            
            return success
        except Exception as e:
            print(f"❌ Error saving session: {e}")
            return False
    
    def _apply_fingerprinting_protections(self, user_agent):
        """Apply anti-fingerprinting measures to make automation less detectable.
        
        Args:
            user_agent (str): The user agent to use.
        """
        if not self.driver:
            return
        
        # Override user agent at the CDP level
        self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
            "userAgent": user_agent,
            "acceptLanguage": "en-US,en;q=0.9",
            "platform": "Win32"
        })
        
        # Remove webdriver property
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        # Select a random GPU vendor/renderer pair
        vendor_renderer_pairs = [
            ('Intel Inc.', 'Intel Iris Xe Graphics'),
            ('Intel Inc.', 'Intel UHD Graphics 630'),
            ('Intel Inc.', 'Intel HD Graphics 520'),
            ('NVIDIA Corporation', 'NVIDIA GeForce GTX 1660 Ti'),
            ('NVIDIA Corporation', 'NVIDIA GeForce RTX 3060'),
            ('AMD', 'AMD Radeon RX 6600 XT'),
            ('AMD', 'AMD Radeon Vega 8'),
        ]
        
        vendor, renderer = random.choice(vendor_renderer_pairs)
        
        # Override WebGL properties to mask fingerprinting
        self.driver.execute_script(f"""
        Object.defineProperty(navigator, 'plugins', {{ get: () => [1,2,3] }});
        Object.defineProperty(navigator, 'languages', {{ get: () => ['en-US', 'en'] }});
        const getParameter = WebGLRenderingContext.prototype.getParameter;
        WebGLRenderingContext.prototype.getParameter = function(param) {{
            if (param === 37445) return '{vendor}';
            if (param === 37446) return '{renderer}';
            return getParameter.call(this, param);
        }};
        """)
