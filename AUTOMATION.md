# ESG News Automation

## Overview
This repository uses GitHub Actions to automatically update ESG news stories 3 times per day.

## Update Schedule
- **6:00 AM Eastern Time** (11:00 AM UTC)
- **12:00 PM Eastern Time** (5:00 PM UTC)  
- **6:00 PM Eastern Time** (11:00 PM UTC)

## What Happens During Each Update

### 1. RSS Feed Generation
- Fetches latest stories from 8 Google Alerts
- Fetches stories from external RSS feeds
- Categorizes articles by topic (carbon, renewable, datacenters, esg, technology, supplychain, rto)
- Generates timestamped RSS feed files

### 2. Website Update
- Creates new timestamped feed file (e.g., `feed-20250822-185335.xml`)
- Updates `esg-news.html` to point to latest feed
- Commits and pushes changes to GitHub
- Updates live website at https://www.sustain74.com/esg-news.html

### 3. CSV Export
- Generates CSV file with all stories and tags
- Saves to local Downloads folder (when run manually)
- Contains: Date, Title, Description, Link, Source, Categories, Tags

## Manual Updates
You can also trigger updates manually:
1. Go to GitHub repository
2. Click "Actions" tab
3. Select "RSS Feed Update" workflow
4. Click "Run workflow" button

## Sources Included

### Google Alerts
- ESG & Energy
- CAISO (California grid)
- ERCOT (Texas grid)
- Carbon Credits
- OBBBA Renewables
- SBTi (Science Based Targets)
- PJM Interconnection
- Additional Feed

### External RSS Feeds
- Climate Change News
- ESG Today
- Corporate Knights
- Data Center Knowledge
- TechRepublic Sustainability
- TechCrunch AI

## File Structure
```
.github/workflows/rss-update.yml  # GitHub Actions workflow
rss_aggregator.py                 # Main RSS aggregation script
esg-news.html                     # News display page
feed-YYYYMMDD-HHMM.xml           # Timestamped RSS feeds
requirements.txt                  # Python dependencies
```

## Monitoring
- Check GitHub Actions tab for update status
- View logs for any errors
- Monitor website for fresh content
- CSV files available in Downloads folder (manual runs)

## Troubleshooting
If updates fail:
1. Check GitHub Actions logs
2. Verify RSS feed sources are accessible
3. Ensure repository has proper permissions
4. Check for Python dependency issues
