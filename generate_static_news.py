#!/usr/bin/env python3
"""
Generate static HTML news page from RSS feed
This creates a version that doesn't require JavaScript to display content
"""

import xml.etree.ElementTree as ET
import re
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from email.utils import parsedate_to_datetime
from urllib.parse import urlparse, parse_qs

def extract_real_website(google_url):
    """Extract the actual destination website from Google Alert URL"""
    try:
        parsed = urlparse(google_url)
        if parsed.hostname == 'www.google.com':
            # Extract the real URL from query parameters
            query_params = parse_qs(parsed.query)
            if 'url' in query_params:
                real_url = query_params['url'][0]
                real_parsed = urlparse(real_url)
                return real_parsed.hostname.replace('www.', '')
        return parsed.hostname.replace('www.', '')
    except:
        return 'unknown'

def clean_source_name(source):
    """Clean up the source name for display"""
    return source.replace('Google Alert: ', '')

def format_date(date_str):
    """Format the date for display"""
    try:
        # Parse RFC 2822 date with timezone and show date component
        dt = parsedate_to_datetime(date_str)
        return dt.astimezone(ZoneInfo('America/New_York')).strftime('%b %d, %Y')
    except Exception:
        return date_str

def clean_title(title):
    """Clean HTML entities from title"""
    # Remove HTML tags
    title = re.sub(r'<[^>]+>', '', title)
    # Decode HTML entities
    title = title.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
    title = title.replace('&quot;', '"').replace('&#39;', "'")
    return title

def generate_static_news_page():
    """Generate static HTML page with embedded news content"""
    
    # Parse the RSS feed
    try:
        tree = ET.parse('feed.xml')
        root = tree.getroot()
    except Exception as e:
        print(f"Error parsing feed.xml: {e}")
        return
    
    # Extract articles
    articles = []
    for item in root.findall('.//item'):
        title = clean_title(item.find('title').text)
        link = item.find('link').text
        pub_date = item.find('pubDate').text
        source = item.find('source').text
        website = extract_real_website(link)
        
        articles.append({
            'title': title,
            'link': link,
            'pub_date': pub_date,
            'source': source,
            'website': website
        })
    
    # Sort by date (newest first)
    articles.sort(key=lambda x: x['pub_date'], reverse=True)
    
    # Generate HTML
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sustain74 ESG News Feed</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f5f5f5;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 30px;
            padding: 20px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .header h1 {{
            color: #2c5aa0;
            margin-bottom: 10px;
        }}
        
        .stats {{
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-top: 15px;
            font-size: 14px;
            color: #666;
        }}
        
        .news-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 20px;
        }}
        
        .news-card {{
            background: white;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            transition: transform 0.2s ease;
        }}
        
        .news-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }}
        
        .news-meta {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
            font-size: 12px;
            color: #666;
        }}
        
        .source {{
            background: #e3f2fd;
            color: #1976d2;
            padding: 2px 8px;
            border-radius: 12px;
            font-weight: 500;
        }}
        
        .date {{
            color: #999;
        }}
        
        h3 {{
            margin-bottom: 10px;
            font-size: 16px;
            line-height: 1.4;
            text-align: left;
        }}
        
        h3 a {{
            color: #333;
            text-decoration: none;
        }}
        
        h3 a:hover {{
            color: #2c5aa0;
        }}
        
        .website {{
            font-size: 12px;
            color: #666;
            margin-top: 8px;
            font-style: italic;
        }}
        
        .loading {{
            text-align: center;
            padding: 40px;
            color: #666;
        }}
        
        @media (max-width: 768px) {{
            .news-grid {{
                grid-template-columns: 1fr;
            }}
            
            .stats {{
                flex-direction: column;
                gap: 10px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Sustain74 ESG News Feed</h1>
            <p>Latest ESG and sustainability news curated by Sustain74</p>
            <div class="stats">
                <span>📊 {len(articles)} Articles</span>
                <span>🕒 Last Updated: {datetime.now(timezone.utc).astimezone(ZoneInfo('America/New_York')).strftime('%B %d, %Y at %I:%M %p %Z')}</span>
            </div>
        </div>
        
        <div class="news-grid">
"""
    
    # Add each article
    for article in articles:
        html_content += f"""
            <div class="news-card">
                <div class="news-meta">
                    <span class="source">{clean_source_name(article['source'])}</span>
                    <span class="date">{format_date(article['pub_date'])}</span>
                </div>
                <h3><a href="{article['link']}" target="_blank" rel="noopener noreferrer">{article['title']}</a></h3>
                <div class="website">{article['website']}</div>
            </div>
"""
    
    html_content += """
        </div>
    </div>
</body>
</html>
"""
    
    # Write to file
    with open('esg-news-static.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ Generated static news page with {len(articles)} articles")
    print("📄 File: esg-news-static.html")

if __name__ == "__main__":
    generate_static_news_page()


