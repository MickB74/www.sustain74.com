#!/usr/bin/env python3
"""
Simple ESG News Update Script
One command to update everything and deploy to live site
"""

import os
import sys
import subprocess
import datetime
from pathlib import Path

def main():
    """Update ESG news and deploy to live site"""
    print("🚀 Sustain74 ESG News Update")
    print("=" * 50)
    
    # Change to the correct directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    print(f"📁 Working in: {os.getcwd()}")
    
    # Step 1: Run RSS aggregator
    print("\n📡 Step 1: Fetching latest ESG news...")
    result = subprocess.run([sys.executable, "rss_aggregator.py"], capture_output=True, text=True)
    
    if result.returncode != 0:
        print("❌ Error running RSS aggregator:")
        print(result.stderr)
        return False
    
    print("✅ News content updated successfully!")
    
    # Step 2: Check for changes
    print("\n🔍 Step 2: Checking for changes...")
    result = subprocess.run("git status --porcelain", shell=True, capture_output=True, text=True)
    
    if not result.stdout.strip():
        print("ℹ️ No new changes detected")
        return True
    
    # Step 3: Deploy to live site
    print("\n🚀 Step 3: Deploying to live website...")
    
    # Add changes
    subprocess.run("git add esg-news-static.html feed.xml", shell=True)
    
    # Commit with timestamp
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    commit_msg = f"Update ESG news - {timestamp}"
    subprocess.run(f'git commit -m "{commit_msg}"', shell=True)
    
    # Push to live site
    result = subprocess.run("git push origin master", shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Successfully deployed to live website!")
        print(f"🌐 View at: https://www.sustain74.com/esg-news-static.html")
    else:
        print("❌ Error deploying to website:")
        print(result.stderr)
        return False
    
    print("\n🎉 Update complete!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)






