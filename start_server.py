#!/usr/bin/env python3
"""
Startup script for the ESG News Flask server
"""

import subprocess
import sys
import os

def install_requirements():
    """Install Flask requirements"""
    print("Installing Flask requirements...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements_flask.txt'])
        print("✅ Flask requirements installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing Flask requirements: {e}")
        return False
    return True

def start_server():
    """Start the Flask server"""
    print("Starting Flask server...")
    print("🌐 Server will be available at: http://localhost:5000")
    print("📰 ESG News page: http://localhost:5000/")
    print("📊 RSS Feed: http://localhost:5000/feed.xml")
    print("\nPress Ctrl+C to stop the server")
    
    try:
        from app import app
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
    except Exception as e:
        print(f"❌ Error starting server: {e}")

if __name__ == '__main__':
    if install_requirements():
        start_server()
    else:
        print("Failed to install requirements. Exiting.")
        sys.exit(1)
