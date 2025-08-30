#!/usr/bin/env python3
"""
Flask app for Sustain74 ESG News
"""

from flask import Flask, render_template_string, send_from_directory, request
import feedparser
import os
from datetime import datetime
import glob

app = Flask(__name__)

# RSS feed URL
RSS_FEED_URL = 'http://localhost:5001/feed.xml'

@app.route('/')
def index():
    """Main ESG news page"""
    try:
        # Fetch latest articles from RSS feed
        feed = feedparser.parse(RSS_FEED_URL)
        articles = []
        
        for entry in feed.entries[:10]:  # Show latest 10 articles
            article = {
                'title': entry.title,
                'description': entry.get('summary', ''),
                'link': entry.link,
                'published': entry.get('published', ''),
                'source': entry.get('source', 'Unknown')
            }
            articles.append(article)
        
        # Get latest TLDR summary
        tldr_files = glob.glob('tldr_summary_*.txt')
        latest_tldr = None
        if tldr_files:
            latest_tldr_file = max(tldr_files, key=os.path.getctime)
            try:
                with open(latest_tldr_file, 'r', encoding='utf-8') as f:
                    latest_tldr = f.read()
            except Exception as e:
                print(f"Error reading TLDR file: {e}")
        
        return render_template_string(HTML_TEMPLATE, articles=articles, tldr=latest_tldr)
        
    except Exception as e:
        return f"Error loading news: {e}", 500

@app.route('/feed.xml')
def rss_feed():
    """Serve the RSS feed"""
    try:
        with open('feed.xml', 'r', encoding='utf-8') as f:
            return f.read(), 200, {'Content-Type': 'application/xml'}
    except FileNotFoundError:
        return "RSS feed not found", 404

@app.route('/assets/<path:filename>')
def assets(filename):
    """Serve static assets"""
    return send_from_directory('assets', filename)

@app.route('/css/<path:filename>')
def css(filename):
    """Serve CSS files"""
    return send_from_directory('css', filename)

@app.route('/js/<path:filename>')
def js(filename):
    """Serve JavaScript files"""
    return send_from_directory('js', filename)

# HTML template for the main page
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sustain74 - ESG News & Insights</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #2c5530;
            text-align: center;
            margin-bottom: 30px;
        }
        .tldr-section {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
            border-left: 4px solid #28a745;
        }
        .tldr-title {
            color: #28a745;
            font-weight: bold;
            margin-bottom: 15px;
        }
        .articles-section h2 {
            color: #2c5530;
            border-bottom: 2px solid #28a745;
            padding-bottom: 10px;
        }
        .article {
            margin-bottom: 25px;
            padding: 15px;
            border: 1px solid #e9ecef;
            border-radius: 5px;
            background: #fafafa;
        }
        .article-title {
            color: #2c5530;
            font-weight: bold;
            margin-bottom: 8px;
        }
        .article-title a {
            color: inherit;
            text-decoration: none;
        }
        .article-title a:hover {
            color: #28a745;
        }
        .article-meta {
            color: #6c757d;
            font-size: 0.9em;
            margin-bottom: 8px;
        }
        .article-description {
            color: #495057;
        }
        .footer {
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #e9ecef;
            color: #6c757d;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🌱 Sustain74 ESG News & Insights</h1>
        
        {% if tldr %}
        <div class="tldr-section">
            <div class="tldr-title">📊 Today's TLDR Summary</div>
            <pre style="white-space: pre-wrap; font-family: inherit; margin: 0;">{{ tldr }}</pre>
        </div>
        {% endif %}
        
        <div class="articles-section">
            <h2>📰 Latest ESG News</h2>
            {% for article in articles %}
            <div class="article">
                <div class="article-title">
                    <a href="{{ article.link }}" target="_blank">{{ article.title }}</a>
                </div>
                <div class="article-meta">
                    📅 {{ article.published }} | 📰 {{ article.source }}
                </div>
                <div class="article-description">
                    {{ article.description[:200] }}{% if article.description|length > 200 %}...{% endif %}
                </div>
            </div>
            {% endfor %}
        </div>
        
        <div class="footer">
            <p>🌐 <a href="/feed.xml">RSS Feed</a> | 📧 <a href="mailto:info@sustain74.com">Contact</a></p>
            <p>Powered by Sustain74 - ESG News & Insights</p>
        </div>
    </div>
</body>
</html>
'''

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
