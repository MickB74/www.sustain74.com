#!/usr/bin/env python3
"""
ESG News Automation Management Script
Control the automated daily updates
"""

import subprocess
import sys
import os

def run_command(command):
    """Run a command and return the result"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_status():
    """Check if automation is running"""
    success, stdout, stderr = run_command("launchctl list | grep com.sustain74.esg-update")
    if success and "com.sustain74.esg-update" in stdout:
        print("✅ Automation is ACTIVE - Updates will run at 8 AM and 12 PM daily")
        return True
    else:
        print("❌ Automation is INACTIVE")
        return False

def start_automation():
    """Start the automation"""
    print("🚀 Starting ESG news automation...")
    success, stdout, stderr = run_command("launchctl load ~/Library/LaunchAgents/com.sustain74.esg-update.plist")
    if success:
        print("✅ Automation started successfully!")
        print("📅 Updates will run daily at 8:00 AM and 12:00 PM")
    else:
        print(f"❌ Failed to start automation: {stderr}")

def stop_automation():
    """Stop the automation"""
    print("🛑 Stopping ESG news automation...")
    success, stdout, stderr = run_command("launchctl unload ~/Library/LaunchAgents/com.sustain74.esg-update.plist")
    if success:
        print("✅ Automation stopped successfully!")
    else:
        print(f"❌ Failed to stop automation: {stderr}")

def run_manual_update():
    """Run a manual update"""
    print("🔄 Running manual ESG news update...")
    success, stdout, stderr = run_command("python automated_update.py")
    if success:
        print("✅ Manual update completed successfully!")
    else:
        print(f"❌ Manual update failed: {stderr}")

def show_logs():
    """Show recent automation logs"""
    print("📋 Recent automation logs:")
    print("-" * 50)
    try:
        with open('automation.log', 'r') as f:
            lines = f.readlines()
            # Show last 20 lines
            for line in lines[-20:]:
                print(line.strip())
    except FileNotFoundError:
        print("No automation logs found yet.")

def main():
    """Main menu"""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
    else:
        command = ""

    if command == "start":
        start_automation()
    elif command == "stop":
        stop_automation()
    elif command == "status":
        check_status()
    elif command == "update":
        run_manual_update()
    elif command == "logs":
        show_logs()
    else:
        print("🌱 Sustain74 ESG News Automation Manager")
        print("=" * 50)
        print("Usage: python manage_automation.py [command]")
        print()
        print("Commands:")
        print("  start   - Start daily automation (8 AM & 12 PM)")
        print("  stop    - Stop daily automation")
        print("  status  - Check if automation is running")
        print("  update  - Run manual update now")
        print("  logs    - Show recent automation logs")
        print()
        check_status()

if __name__ == "__main__":
    main()
