
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
    </style>
</head>
<body>
    <div class="container">
        <h1>Browser Session Manager</h1>
        <p>This application requires a graphical interface and cannot run directly in the web browser.</p>
        <p>Please run this application in the Replit workspace using the Run button.</p>
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
