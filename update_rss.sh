#!/bin/bash

# RSS Feed Update Script for Sustain74
# This script is designed to be run by cron

# Change to the website directory
cd /Users/michaelbarry/Documents/GitHub/www.sustain74.com

# Log file for debugging
LOG_FILE="/Users/michaelbarry/Documents/GitHub/www.sustain74.com/rss_update.log"

# Function to log with timestamp
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
}

log "Starting RSS feed update"

# Run the RSS aggregator using full path to conda python
/opt/anaconda3/bin/python rss_aggregator.py >> "$LOG_FILE" 2>&1

if [ $? -eq 0 ]; then
    log "RSS feed updated successfully"
    
    # Optional: Upload to your web server if needed
    # You can uncomment and modify these lines if you need to upload the feed.xml to a server
    # scp feed.xml user@yourserver.com:/path/to/website/
    # rsync -av feed.xml user@yourserver.com:/path/to/website/
    
else
    log "ERROR: RSS feed update failed"
fi

log "RSS feed update completed"
