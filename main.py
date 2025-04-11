
"""
Browser Session Manager
-----------------------
A GUI application for managing browser sessions, profiles, and automating browser interactions.
"""
import os
import sys
from flask import Flask, render_template_string
from gui.app import BrowserSessionManagerApp

app = Flask(__name__)
app.secret_key = os.environ.get('SESSION_SECRET', os.urandom(24))

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Browser Session Manager</title>
    <style>
        body { font-family: Arial; background: #2b2b2b; color: white; margin: 20px; }
        .container { max-width: 800px; margin: 0 auto; background: #363636; padding: 20px; border-radius: 8px; }
        .btn { 
            display: inline-block; 
            background: #007bff; 
            color: white; 
            padding: 10px 20px; 
            text-decoration: none; 
            border-radius: 4px; 
            margin-top: 20px;
            font-weight: bold; 
        }
        .btn:hover { background: #0056b3; }
        .info { background: #363636; border-left: 4px solid #42a5f5; padding: 10px 15px; margin: 15px 0; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Browser Session Manager</h1>
        <p>This application now has both a desktop version and a web interface version:</p>
        
        <div class="info">
            <h2>Web Version (Recommended)</h2>
            <p>The newer web-based version of Browser Session Manager is now available.</p>
            <a href="/?workflow=browser_session_manager_nodejs" class="btn">Access Web Version</a>
        </div>
        
        <div class="info">
            <h2>Desktop Version</h2>
            <p>The original Python desktop application requires a graphical interface and cannot run directly in the browser.</p>
            <p>To use the desktop version, run the "standalone_browser_manager" workflow in the Replit workspace.</p>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

def main():
    """Main entry point for the Browser Session Manager application."""
    if os.environ.get('REPL_SLUG'):  # Running in deployment
        port = int(os.environ.get('PORT', 8080))
        app.run(host='0.0.0.0', port=port)
    else:  # Running in development
        browser_app = BrowserSessionManagerApp()
        browser_app.run()

if __name__ == "__main__":
    main()
