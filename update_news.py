#!/usr/bin/env python3
"""
Simple ESG News Update Script
One command to update everything and deploy to live site
"""

import os
import sys
import subprocess
import datetime
from datetime import timezone
from zoneinfo import ZoneInfo
import re
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
    
    # Step 2: Update ESG News links with cache-busting query
    print("\n🧹 Step 2: Updating ESG News links with cache-busting query...")
    try:
        version = datetime.datetime.now(timezone.utc).astimezone(ZoneInfo('America/New_York')).strftime('%Y%m%d-%H%M')
        pattern = re.compile(r'(esg-news-static\.html)(?:\?v=[^"\'>\s)]*)?')
        changed_files = []
        for root, _, files in os.walk('.'):
            for fname in files:
                if not fname.endswith('.html'):
                    continue
                fpath = os.path.join(root, fname)
                try:
                    with open(fpath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    new_content = pattern.sub(rf"\1?v={version}", content)
                    if new_content != content:
                        with open(fpath, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        changed_files.append(fpath)
                except Exception:
                    continue
        if changed_files:
            print(f"✅ Updated cache-busting on {len(changed_files)} file(s)")
        else:
            print("ℹ️ No ESG News links found to update")
    except Exception as e:
        print(f"⚠️ Could not update cache-busting links: {e}")

    # Step 3: Check for changes
    print("\n🔍 Step 3: Checking for changes...")
    result = subprocess.run("git status --porcelain", shell=True, capture_output=True, text=True)
    
    if not result.stdout.strip():
        print("ℹ️ No new changes detected")
        return True
    
    # Step 4: Deploy to live site
    print("\n🚀 Step 4: Deploying to live website...")
    
    # Add changes
    subprocess.run("git add -A", shell=True)
    
    # Commit with timestamp
    timestamp = datetime.datetime.now(timezone.utc).astimezone(ZoneInfo('America/New_York')).strftime('%Y-%m-%d %H:%M %Z')
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






