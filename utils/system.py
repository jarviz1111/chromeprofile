"""
System Utilities Module
----------------------
Handles system-level operations such as process management.
"""
import psutil

def kill_chrome_processes():
    """Kill all running Chrome and ChromeDriver processes."""
    try:
        # Target process names to kill
        target_processes = [
            "chrome.exe", 
            "chromedriver.exe",
            "chrome",
            "chromedriver"
        ]
        
        killed_count = 0
        for proc in psutil.process_iter():
            try:
                # Check if process name contains one of the target names
                proc_name = proc.name().lower()
                if any(target in proc_name for target in target_processes):
                    proc.kill()
                    killed_count += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        if killed_count > 0:
            print(f"🧹 Cleaned up {killed_count} Chrome processes.")
        
        return killed_count
    except Exception as e:
        print(f"⚠️ Error killing Chrome processes: {e}")
        return 0
