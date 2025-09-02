#!/usr/bin/env python3
"""
Flask app for Sustain74 ESG News
"""

from flask import Flask, render_template_string, send_from_directory, request, jsonify
import feedparser
import os
from datetime import datetime
import glob
import subprocess
import sys

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# RSS feed URL
RSS_FEED_URL = 'http://localhost:5001/feed.xml'

@app.route('/')
def index():
    """Main ESG news page"""
    try:
        # Determine current feed version (mtime) for auto-refresh logic
        try:
            feed_version = int(os.path.getmtime(os.path.join(BASE_DIR, 'feed.xml')))
        except Exception:
            feed_version = 0
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
        tldr_files = glob.glob(os.path.join(BASE_DIR, 'tldr_summary_*.txt'))
        latest_tldr = None
        if tldr_files:
            latest_tldr_file = max(tldr_files, key=os.path.getctime)
            try:
                with open(latest_tldr_file, 'r', encoding='utf-8') as f:
                    latest_tldr = f.read()
            except Exception as e:
                print(f"Error reading TLDR file: {e}")
        
        return render_template_string(HTML_TEMPLATE, articles=articles, tldr=latest_tldr, feed_version=feed_version)
        
    except Exception as e:
        return f"Error loading news: {e}", 500

@app.route('/feed.xml')
def rss_feed():
    """Serve the RSS feed"""
    try:
        feed_path = os.path.join(BASE_DIR, 'feed.xml')
        with open(feed_path, 'r', encoding='utf-8') as f:
            return f.read(), 200, {
                'Content-Type': 'application/xml',
                'Cache-Control': 'no-store, max-age=0',
                'Pragma': 'no-cache'
            }
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

# Lightweight status endpoint used by the homepage to detect when a refresh completes
@app.route('/status')
def status():
    try:
        version = int(os.path.getmtime(os.path.join(BASE_DIR, 'feed.xml')))
    except Exception:
        version = 0
    return jsonify({ 'feed_version': version })

# Admin endpoint to refresh stories and TLDR
@app.route('/admin/refresh', methods=['POST'])
def admin_refresh():
    """Kick off rss_aggregator.py in the background and return immediately"""
    try:
        app_dir = os.path.dirname(os.path.abspath(__file__))
        log_path = os.path.join(app_dir, 'refresh.log')
        # Append to a simple log file for visibility
        with open(log_path, 'a') as log_file:
            log_file.write(f"\n=== Refresh requested at {datetime.now().isoformat()} ===\n")
            subprocess.Popen(
                [sys.executable, 'rss_aggregator.py'],
                cwd=app_dir,
                stdout=log_file,
                stderr=log_file,
            )
        return ("Refresh started", 202)
    except Exception as e:
        return (f"Error starting refresh: {e}", 500)

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
        <div style="text-align: right; margin: 10px 0 20px 0;">
            <button id="refreshBtn" style="background:#2c5530;color:#fff;border:none;padding:8px 12px;border-radius:6px;cursor:pointer;">↻ Refresh stories & TLDR</button>
            <span id="refreshStatus" style="margin-left:10px;color:#6c757d;"></span>
        </div>
        
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
    <script>
    // Current content version (feed.xml mtime) rendered by server
    var INITIAL_FEED_VERSION = {{ feed_version if feed_version is not none else 0 }};
    (function() {
        var btn = document.getElementById('refreshBtn');
        if (!btn) return;
        var statusEl = document.getElementById('refreshStatus');
        btn.addEventListener('click', function() {
            btn.disabled = true;
            if (statusEl) statusEl.textContent = 'Starting refresh...';
            fetch('/admin/refresh', { method: 'POST' })
                .then(function(res) {
                    if (res.status === 202) {
                        if (statusEl) statusEl.textContent = 'Refreshing... this will auto-reload when ready.';
                        // Poll status endpoint for updated version
                        var attempts = 0;
                        var maxAttempts = 60; // ~5 minutes at 5s interval
                        var poll = setInterval(function() {
                            fetch('/status', { cache: 'no-store' })
                                .then(function(r){ return r.json(); })
                                .then(function(data){
                                    if (!data) return;
                                    if (data.feed_version && data.feed_version > INITIAL_FEED_VERSION) {
                                        if (statusEl) statusEl.textContent = 'Update ready. Reloading...';
                                        clearInterval(poll);
                                        window.location.reload();
                                    } else if (++attempts >= maxAttempts) {
                                        clearInterval(poll);
                                        if (statusEl) statusEl.textContent = 'Timeout waiting for update. Please reload.';
                                        btn.disabled = false;
                                    }
                                })
                                .catch(function(){ /* ignore transient errors */ });
                        }, 5000);
                    } else {
                        return res.text().then(function(t) {
                            if (statusEl) statusEl.textContent = 'Error: ' + t;
                        });
                    }
                })
                .catch(function() {
                    if (statusEl) statusEl.textContent = 'Network error starting refresh';
                })
                .finally(function() {
                    // Button remains disabled until success or timeout above
                });
        });
    })();
    </script>
</body>
</html>
'''

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)







