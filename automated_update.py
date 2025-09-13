#!/usr/bin/env python3
"""
Automated ESG News Update Script
Runs RSS aggregator, commits changes, and pushes to live site
"""

import os
import sys
import subprocess
import datetime
from pathlib import Path

def log_message(message):
    """Log message with timestamp"""
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {message}")
    
    # Also write to log file
    with open('automation.log', 'a') as f:
        f.write(f"[{timestamp}] {message}\n")

def run_command(command, description):
    """Run a command and log the result"""
    log_message(f"Starting: {description}")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=os.getcwd())
        if result.returncode == 0:
            log_message(f"✅ Success: {description}")
            if result.stdout:
                log_message(f"Output: {result.stdout.strip()}")
        else:
            log_message(f"❌ Error: {description}")
            log_message(f"Error output: {result.stderr.strip()}")
            return False
    except Exception as e:
        log_message(f"❌ Exception in {description}: {str(e)}")
        return False
    return True

def main():
    """Main automation function"""
    log_message("🚀 Starting automated ESG news update")
    
    # Change to the correct directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    log_message(f"Working directory: {os.getcwd()}")
    
    # Step 1: Run RSS aggregator
    if not run_command("python rss_aggregator.py", "RSS Aggregator"):
        log_message("❌ RSS Aggregator failed, stopping automation")
        return False
    
    # Step 2: Check if there are changes to commit
    result = subprocess.run("git status --porcelain", shell=True, capture_output=True, text=True)
    if not result.stdout.strip():
        log_message("ℹ️ No changes detected, nothing to commit")
        return True
    
    # Step 3: Add all changes
    if not run_command("git add .", "Git add changes"):
        return False
    
    # Step 4: Commit changes
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    commit_message = f"Automated update - {timestamp}"
    if not run_command(f'git commit -m "{commit_message}"', "Git commit"):
        return False
    
    # Step 5: Push to live site
    if not run_command("git push origin master", "Git push to live site"):
        return False
    
    log_message("🎉 Automated update completed successfully!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)












