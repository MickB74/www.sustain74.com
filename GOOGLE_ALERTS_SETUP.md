# Google Alerts Integration Setup Guide

This guide will help you set up Google Alerts to automatically feed ESG and sustainability news to your Sustain74 website.

## Overview

The news section on Sustain74.com is designed to integrate with Google Alerts RSS feeds to provide real-time ESG and sustainability news updates. This system includes:

- **Frontend**: A responsive news page with filtering and categorization
- **Backend**: Python script to fetch and process RSS feeds
- **Caching**: Local caching to improve performance and reduce API calls

## Step 1: Set Up Google Alerts

### 1.1 Create Google Alerts

1. Go to [Google Alerts](https://www.google.com/alerts)
2. Sign in with your Google account
3. Create alerts for the following recommended keywords:

#### Primary ESG Keywords:
- "ESG reporting"
- "sustainability regulations"
- "climate disclosure"
- "renewable energy investment"
- "carbon neutrality"

#### Secondary Keywords:
- "sustainable finance"
- "green bonds"
- "net zero commitments"
- "SBTi scope 3"
- "CDP reporting"
- "ESG regulations"
- "sustainability standards"
- "clean energy transition"
- "circular economy"
- "climate risk disclosure"

### 1.2 Configure Alert Settings

For each alert, set the following:
- **Frequency**: "As-it-happens" or "Once a day"
- **Sources**: "Automatic" (includes news, blogs, discussions)
- **Language**: English
- **Region**: United States (or your target region)
- **How many**: "All results"
- **Deliver to**: "RSS feed"

### 1.3 Get RSS Feed URLs

1. After creating each alert, click on the alert name
2. Look for the "RSS" link or icon
3. Copy the RSS feed URL (it will look like: `https://www.google.com/alerts/feeds/12345678901234567890/12345678901234567890`)
4. Save these URLs for the next step

## Step 2: Configure the Backend

### 2.1 Install Dependencies

```bash
pip install -r requirements.txt
```

### 2.2 Update RSS Feed URLs

Edit the `google_alerts_fetcher.py` file and add your RSS feed URLs:

```python
self.rss_feeds = [
    "https://www.google.com/alerts/feeds/YOUR_FEED_ID_1",
    "https://www.google.com/alerts/feeds/YOUR_FEED_ID_2",
    "https://www.google.com/alerts/feeds/YOUR_FEED_ID_3",
    # Add more as needed
]
```

### 2.3 Test the Setup

Run the Python script to test the integration:

```bash
python google_alerts_fetcher.py
```

You should see output showing the articles fetched from your Google Alerts.

## Step 3: Integration Options

### Option A: Static Integration (Recommended for Simple Setup)

1. Run the Python script periodically (e.g., daily via cron job)
2. The script will create a `news_cache.json` file
3. Update your JavaScript to read from this cache file

### Option B: Dynamic Integration (Advanced)

1. Set up a web server (Flask/FastAPI) to serve the news data
2. Create an API endpoint that runs the fetcher on demand
3. Update the JavaScript to fetch from your API endpoint

## Step 4: Customization

### 4.1 Add Custom Keywords

Edit the `recommended_keywords` list in `google_alerts_fetcher.py`:

```python
self.recommended_keywords = [
    "ESG reporting",
    "sustainability regulations",
    # Add your custom keywords here
    "your custom keyword",
]
```

### 4.2 Modify Categories

Update the `keyword_mappings` in the `categorize_article` method:

```python
keyword_mappings = {
    'esg': ['esg', 'environmental social governance'],
    'climate': ['climate', 'carbon', 'emissions'],
    'renewable': ['renewable', 'solar', 'wind'],
    'regulations': ['regulation', 'compliance', 'sec'],
    'sustainability': ['sustainability', 'sustainable'],
    # Add your custom categories
    'your_category': ['your', 'keywords'],
}
```

### 4.3 Adjust Cache Settings

Modify the cache duration in `load_from_cache`:

```python
# Change from 1 hour to your preferred duration
if datetime.now() - cache_time < timedelta(hours=6):  # 6 hours
```

## Step 5: Automation

### 5.1 Cron Job Setup (Linux/Mac)

Add to your crontab (`crontab -e`):

```bash
# Update news every 6 hours
0 */6 * * * cd /path/to/sustain74 && python google_alerts_fetcher.py
```

### 5.2 Windows Task Scheduler

1. Open Task Scheduler
2. Create a new Basic Task
3. Set trigger to run every 6 hours
4. Set action to run: `python google_alerts_fetcher.py`
5. Set start in: `/path/to/sustain74`

## Step 6: Monitoring and Maintenance

### 6.1 Check Logs

The script logs its activity. Monitor the output for:
- Successful RSS feed fetches
- Error messages
- Cache updates

### 6.2 Update Keywords

Periodically review and update your Google Alerts keywords based on:
- Industry trends
- New regulations
- Client interests
- Performance metrics

### 6.3 Performance Optimization

- Monitor cache file size
- Adjust fetch frequency based on traffic
- Consider implementing rate limiting for RSS feeds

## Troubleshooting

### Common Issues

1. **No articles appearing**
   - Check RSS feed URLs are correct
   - Verify Google Alerts are active
   - Check internet connectivity

2. **Duplicate articles**
   - The script automatically removes duplicates
   - Check if multiple alerts have overlapping keywords

3. **Slow loading**
   - Increase cache duration
   - Reduce fetch frequency
   - Check server performance

### Error Messages

- `Error fetching RSS feed`: Check feed URL and internet connection
- `Error parsing RSS entry`: Feed format may have changed
- `Error saving to cache`: Check file permissions

## Advanced Features

### Email Integration

Google Alerts can also send email notifications. You can:
1. Set up email forwarding to a dedicated address
2. Use email parsing libraries to extract article data
3. Integrate with the existing RSS system

### Multiple Sources

Consider adding other news sources:
- RSS feeds from ESG news sites
- API integrations (NewsAPI, etc.)
- Social media feeds (Twitter, LinkedIn)

### Analytics

Track news performance:
- Most popular categories
- Click-through rates
- User engagement metrics

## Support

For technical support or questions about this integration, contact:
- Email: info@sustain74.com
- Documentation: Check the code comments in `google_alerts_fetcher.py`

## Security Considerations

- Keep RSS feed URLs private
- Implement rate limiting for production use
- Validate and sanitize all incoming data
- Use HTTPS for all external requests
- Regularly update dependencies

---

**Last Updated**: January 2025
**Version**: 1.0
