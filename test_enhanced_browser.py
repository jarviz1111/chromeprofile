"""
Test Enhanced Browser Session Manager
------------------------------------
This script demonstrates how to use the enhanced browser session features
from the command line, without requiring the GUI interface.
"""

import os
import sys
import time
import json
import argparse
from datetime import datetime

# Import our session utilities
try:
    from utils.session_utils import (
        init_db, save_enhanced_session, load_enhanced_session, 
        get_all_profiles, delete_profile, rename_profile
    )
    print("✅ Imported enhanced session utilities.")
except ImportError:
    print("❌ Enhanced session utilities not found.")
    print("Please make sure utils/session_utils.py exists.")
    sys.exit(1)

# Import required selenium and browser automation libraries
try:
    import undetected_chromedriver as uc
    from selenium.webdriver.chrome.options import Options
    from fake_useragent import UserAgent
except ImportError:
    print("❌ Required libraries not found.")
    print("Please run: pip install undetected-chromedriver selenium fake-useragent")
    sys.exit(1)

def list_profiles():
    """List all saved profiles with enhanced information."""
    print("\n📋 SAVED BROWSER PROFILES:")
    print("=" * 80)
    
    profiles = get_all_profiles()
    if not profiles:
        print("No profiles found in the database.")
        return
    
    for i, profile_data in enumerate(profiles):
        profile_id = profile_data[0]
        updated_at = profile_data[1] if len(profile_data) > 1 else "Unknown"
        email = profile_data[2] if len(profile_data) > 2 else None
        login_domain = profile_data[3] if len(profile_data) > 3 else None
        login_count = profile_data[4] if len(profile_data) > 4 else None
        
        # Format updated date
        if updated_at and updated_at != "Unknown":
            try:
                dt = datetime.fromisoformat(updated_at)
                updated_at = dt.strftime("%Y-%m-%d %H:%M:%S")
            except:
                pass
                
        # Print profile info
        print(f"\n{i+1}. {profile_id}")
        print(f"   Updated: {updated_at}")
        
        if email:
            # Mask part of the email for privacy
            email_preview = f"{email[:3]}...@{email.split('@')[1]}" if '@' in email else f"{email[:3]}..."
            print(f"   Email: {email_preview}")
        
        if login_domain:
            print(f"   Domain: {login_domain}")
            
        if login_count and int(login_count) > 0:
            print(f"   Login Count: {login_count}")
            
    print("\n" + "=" * 80)

def launch_browser(profile_id, proxy=None, headless=False):
    """Launch a browser with the specified profile."""
    # Initialize the database if needed
    init_db()
    
    print(f"🟢 Launching browser for profile: {profile_id}")
    
    # Create profile directory if it doesn't exist
    user_data_dir = os.path.join("browser_profiles", profile_id)
    os.makedirs(user_data_dir, exist_ok=True)
    
    # Load session data from database
    session_data = load_enhanced_session(profile_id)
    login_domain = None
    
    if session_data:
        user_agent = session_data["user_agent"]
        stored_cookies = session_data["cookies"]
        email = session_data.get("email")
        login_domain = session_data.get("login_domain")
        
        # Log some info without revealing sensitive data
        if email:
            email_preview = f"{email[:3]}...@{email.split('@')[1]}" if '@' in email else f"{email[:3]}..."
            print(f"🔑 Using saved credentials for: {email_preview}")
        
        if login_domain:
            print(f"🌐 Account domain: {login_domain}")
    else:
        stored_cookies = None
        # Generate a new user agent
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

    # Configure Chrome options with enhanced anti-detection
    options = uc.ChromeOptions()
    options.add_argument(f"--user-agent={user_agent}")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-infobars")
    
    # Handle headless mode if requested
    if headless:
        options.add_argument("--headless=new")
        print("🖥️ Running in headless mode")
    
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument(f"--user-data-dir={user_data_dir}")
    
    # Load our extension for displaying user agent and IP
    extension_path = os.path.abspath("extensions/info_display")
    if os.path.exists(extension_path):
        print(f"📋 Loading browser info extension from: {extension_path}")
        options.add_argument(f"--load-extension={extension_path}")
    else:
        print("⚠️ Browser info extension not found. Info overlay will not be available.")
    
    # Add proxy if specified
    if proxy:
        options.add_argument(f"--proxy-server=http://{proxy}")
        print(f"🌐 Using Proxy: {proxy}")
    else:
        print("🚫 No proxy set.")

    # Initialize Chrome driver with enhanced arguments
    try:
        driver = uc.Chrome(options=options)
        
        # Apply basic anti-fingerprinting measures
        driver.execute_script("""
        // Hide automation flags
        Object.defineProperty(navigator, 'webdriver', {get: () => undefined})
        
        // Override plugins
        Object.defineProperty(navigator, 'plugins', { get: () => [
            {'name': 'Chrome PDF Plugin', 'filename': 'internal-pdf-viewer', 'description': 'Portable Document Format',
             'length': 1, '0': {'type': 'application/x-google-chrome-pdf', 'suffixes': 'pdf', 'description': 'Portable Document Format'}}
        ] });
        """)
        
        # Open website based on the profile type
        if stored_cookies:
            # Use specific URL based on login domain
            if login_domain == "google.com":
                driver.get("https://accounts.google.com/")
                for cookie in stored_cookies:
                    if 'sameSite' in cookie:
                        del cookie['sameSite']
                    try:
                        driver.add_cookie(cookie)
                    except:
                        pass
                driver.get("https://mail.google.com/")
                print("📧 Navigating to Gmail inbox")
            
            elif login_domain == "yahoo.com":
                driver.get("https://login.yahoo.com/")
                for cookie in stored_cookies:
                    if 'sameSite' in cookie:
                        del cookie['sameSite']
                    try:
                        driver.add_cookie(cookie)
                    except:
                        pass
                driver.get("https://mail.yahoo.com/")
                print("📧 Navigating to Yahoo Mail inbox")
                
            else:
                # Generic approach for other domains
                driver.get("https://accounts.google.com/signup")
                for cookie in stored_cookies:
                    if 'sameSite' in cookie:
                        del cookie['sameSite']
                    try:
                        driver.add_cookie(cookie)
                    except:
                        pass
                driver.get("https://www.google.com")
                print("🌐 Navigating to homepage")
        else:
            # No cookies found, navigate to the login page
            if "gmail" in profile_id.lower() or "google" in profile_id.lower():
                driver.get("https://accounts.google.com/signin")
                print("📧 Navigating to Gmail login page")
            elif "yahoo" in profile_id.lower():
                driver.get("https://login.yahoo.com/")
                print("📧 Navigating to Yahoo login page")
            elif "outlook" in profile_id.lower() or "hotmail" in profile_id.lower():
                driver.get("https://login.live.com/")
                print("📧 Navigating to Outlook login page")
            else:
                driver.get("https://accounts.google.com/signup")
                print("🔄 Navigating to default login page")
                
            print("⚠️ Please login manually...")

        # Keep browser open until user presses Enter
        print("\n✅ Browser launched successfully!")
        print("📋 Press Enter to close the browser and save the session...\n")
        input()
        
        # Save the session before closing
        print("💾 Saving session data...")
        try:
            cookies = driver.get_cookies()
            current_user_agent = driver.execute_script("return navigator.userAgent")
            
            # Try to detect email from Gmail's UI
            email = None
            login_domain = None
            
            current_url = driver.current_url.lower()
            if "gmail" in current_url or "mail.google" in current_url:
                login_domain = "google.com"
                try:
                    # Check Gmail profile information
                    driver.get("https://myaccount.google.com/")
                    time.sleep(2)
                    email_elements = driver.find_elements_by_css_selector("[data-email]")
                    if email_elements:
                        email = email_elements[0].get_attribute("data-email")
                except:
                    pass
            elif "yahoo.com/mail" in current_url:
                login_domain = "yahoo.com"
            elif "outlook.live" in current_url or "outlook.office" in current_url:
                login_domain = "outlook.com"
            
            # Get hardware profile info
            screen_resolution = driver.execute_script("return window.screen.width + 'x' + window.screen.height")
            platform = driver.execute_script("return navigator.platform")
            language = driver.execute_script("return navigator.language")
            
            # Save session with enhanced data
            success = save_enhanced_session(
                profile_id, 
                current_user_agent, 
                cookies,
                email=email,
                login_domain=login_domain,
                screen_resolution=screen_resolution,
                platform=platform,
                language=language
            )
            
            if success:
                print("✅ Session saved successfully!")
            else:
                print("❌ Failed to save session.")
                
        except Exception as e:
            print(f"❌ Error saving session: {e}")
        
        # Close the browser
        print("🔚 Closing browser...")
        driver.quit()
        return True
        
    except Exception as e:
        print(f"❌ Error launching browser: {e}")
        return False

def main():
    """Main function to parse command line arguments and execute commands."""
    parser = argparse.ArgumentParser(description="Enhanced Browser Session Manager CLI")
    
    # Add command argument
    parser.add_argument('command', choices=['list', 'launch', 'delete', 'rename'],
                        help='Command to execute')
    
    # Add optional profile argument
    parser.add_argument('--profile', '-p', type=str, help='Profile name/identifier')
    
    # Add optional proxy argument
    parser.add_argument('--proxy', type=str, help='Proxy to use (format: ip:port or user:pass@ip:port)')
    
    # Add headless mode flag
    parser.add_argument('--headless', action='store_true', help='Run browser in headless mode')
    
    # Add rename arguments
    parser.add_argument('--new-name', type=str, help='New profile name (for rename command)')
    
    args = parser.parse_args()
    
    # Initialize database
    init_db()
    
    # Execute command
    if args.command == 'list':
        list_profiles()
        
    elif args.command == 'launch':
        if not args.profile:
            print("❌ Profile name is required for launch command.")
            parser.print_help()
            return
            
        launch_browser(args.profile, args.proxy, args.headless)
        
    elif args.command == 'delete':
        if not args.profile:
            print("❌ Profile name is required for delete command.")
            parser.print_help()
            return
            
        confirm = input(f"Are you sure you want to delete profile '{args.profile}'? (y/n): ")
        if confirm.lower() == 'y':
            success = delete_profile(args.profile)
            if success:
                print(f"✅ Profile '{args.profile}' deleted successfully.")
            else:
                print(f"❌ Failed to delete profile '{args.profile}'.")
        else:
            print("Operation cancelled.")
            
    elif args.command == 'rename':
        if not args.profile or not args.new_name:
            print("❌ Both profile and new-name are required for rename command.")
            parser.print_help()
            return
            
        success = rename_profile(args.profile, args.new_name)
        if success:
            print(f"✅ Profile renamed from '{args.profile}' to '{args.new_name}'.")
        else:
            print(f"❌ Failed to rename profile.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️ Operation interrupted by user.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")