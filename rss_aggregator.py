







#!/usr/bin/env python3
"""
RSS Feed Aggregator for Sustain74
Fetches relevant ESG/sustainability stories from external sources
"""

import feedparser
import requests
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from email.utils import format_datetime, parsedate_to_datetime
import logging
import xml.etree.ElementTree as ET
import csv
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os
import re
from urllib.parse import urlparse, parse_qs
# AI summary (Gemini) dependencies removed

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RSSAggregator:
    def __init__(self):
        # AI TLDR generation removed; no Gemini configuration
        
        # External RSS feeds - DISABLED - Only using Google Alerts
        self.external_feeds = []
        
        # Google Alerts RSS feeds - Add your Google Alerts RSS URLs here
        # To get Google Alerts RSS URLs:
        # 1. Go to https://www.google.com/alerts
        # 2. Edit each alert and set "Deliver to" to "RSS feed"
        # 3. Copy the RSS URL and add it below
        self.google_alerts_feeds = [
            {
                'url': 'https://www.google.com/alerts/feeds/05477018627257484545/7247076399060117174',
                'name': 'Google Alert: AI and Sustainability',
                'keywords': ['ai', 'artificial intelligence', 'sustainability', 'sustainable energy', 'ai infrastructure', 'data centers', 'carbon footprint', 'environmental ai', 'green technology', 'sustainable ai', 'ai efficiency', 'ai data centers', 'ai power consumption']
            },
            {
                'url': 'https://www.google.com/alerts/feeds/05477018627257484545/2588330808811951080',
                'name': 'Google Alert: CAISO',
                'keywords': ['caiso', 'california independent system operator', 'energy market', 'grid operator', 'ferc', 'day-ahead market', 'energy trading', 'california energy', 'edam', 'extended day-ahead market', 'california grid', 'energy regulation']
            },
            {
                'url': 'https://www.google.com/alerts/feeds/05477018627257484545/9317338791963863020',
                'name': 'Google Alert: Carbon Credits',
                'keywords': ['carbon credits', 'carbon trading', 'carbon offset', 'carbon market', 'vcm', 'voluntary carbon market', 'carbon neutral', 'carbon reduction', 'esg carbon', 'carbon capture', 'co2 removal', 'carbon pricing', 'green crypto', 'tokenized carbon']
            },
            {
                'url': 'https://www.google.com/alerts/feeds/05477018627257484545/17843257093320527979',
                'name': 'Google Alert: EIA',
                'keywords': ['eia', 'energy information administration', 'energy data', 'energy statistics', 'energy reports', 'energy market data', 'electric power monthly', 'natural gas storage', 'oil exports', 'energy forecasts', 'energy outlook', 'energy analysis']
            },
            {
                'url': 'https://www.google.com/alerts/feeds/05477018627257484545/10208059211885938613',
                'name': 'Google Alert: EPA',
                'keywords': ['epa', 'environmental protection agency', 'environmental regulation', 'greenhouse gas reporting', 'emissions standards', 'environmental policy', 'pollution control', 'environmental compliance', 'drinking water standards', 'pfas chemicals', 'carbon capture', 'environmental enforcement']
            },
            {
                'url': 'https://www.google.com/alerts/feeds/05477018627257484545/2588084030416567261',
                'name': 'Google Alert: ERCOT',
                'keywords': ['ercot', 'electric reliability council of texas', 'texas grid', 'texas energy market', 'texas power grid', 'texas electricity', 'texas energy trading', 'texas grid operator', 'texas energy regulation', 'texas power market', 'texas energy policy']
            },
            {
                'url': 'https://www.google.com/alerts/feeds/05477018627257484545/4717940623999380595',
                'name': 'Google Alert: ESG',
                'keywords': ['esg', 'environmental social governance', 'esg reporting', 'esg ratings', 'esg investing', 'esg bonds', 'esg funds', 'esg disclosure', 'sustainability reporting', 'corporate responsibility', 'esg integration', 'greenwashing', 'esg policy', 'esg risk']
            },
            {
                'url': 'https://www.google.com/alerts/feeds/05477018627257484545/2588084030416566838',
                'name': 'Google Alert: ESG Report Release',
                'keywords': ['esg report', 'esg report release', 'sustainability report', 'esg disclosure', 'corporate sustainability', 'esg reporting', 'sustainability disclosure', 'esg annual report', 'esg materiality report', 'esg impact report', 'sustainability materiality', 'esg data reporting']
            },
            {
                'url': 'https://www.google.com/alerts/feeds/05477018627257484545/6227487727411824085',
                'name': 'Google Alert: GHG Protocol',
                'keywords': ['ghg protocol', 'greenhouse gas protocol', 'carbon accounting', 'scope 1 emissions', 'scope 2 emissions', 'scope 3 emissions', 'carbon reporting', 'emissions reporting', 'carbon standards', 'ghg standards', 'carbon measurement', 'emissions measurement', 'carbon footprint', 'ghg accounting']
            },
            {
                'url': 'https://www.google.com/alerts/feeds/05477018627257484545/10834986087919876596',
                'name': 'Google Alert: IEA',
                'keywords': ['iea', 'international energy agency', 'energy outlook', 'energy policy', 'energy security', 'energy transition', 'global energy', 'energy markets', 'energy analysis', 'energy forecasts', 'energy statistics', 'energy reports', 'clean energy transition', 'energy efficiency']
            },
            {
                'url': 'https://www.google.com/alerts/feeds/05477018627257484545/15133328373837915052',
                'name': 'Google Alert: India Renewables',
                'keywords': ['india renewable energy', 'india renewables', 'india solar', 'india wind', 'india clean energy', 'india green energy', 'india sustainable energy', 'india renewable projects', 'india solar power', 'india wind power', 'india energy transition', 'india renewable development', 'india clean power', 'india renewable infrastructure']
            },
            {
                'url': 'https://www.google.com/alerts/feeds/05477018627257484545/3557627759411880609',
                'name': 'Google Alert: LNG',
                'keywords': ['lng', 'liquefied natural gas', 'natural gas', 'gas markets', 'gas trading', 'gas infrastructure', 'gas exports', 'gas imports', 'gas terminals', 'gas pipelines', 'gas storage', 'gas prices', 'gas supply', 'gas demand', 'gas transportation']
            },
            {
                'url': 'https://www.google.com/alerts/feeds/05477018627257484545/11355611965384655818',
                'name': 'Google Alert: Sustainable Aviation Fuel',
                'keywords': ['sustainable aviation fuel', 'saf', 'aviation fuel', 'biofuel', 'renewable jet fuel', 'aviation emissions', 'carbon neutral aviation', 'green aviation', 'sustainable transport', 'aviation sustainability', 'low carbon aviation', 'renewable aviation']
            },
            {
                'url': 'https://www.google.com/alerts/feeds/05477018627257484545/4817184826234460345',
                'name': 'Google Alert: SMR',
                'keywords': ['smr', 'small modular reactor', 'nuclear energy', 'modular nuclear', 'nuclear power', 'clean nuclear', 'advanced nuclear', 'nuclear technology', 'nuclear innovation', 'nuclear safety', 'nuclear waste', 'nuclear fuel', 'nuclear reactor', 'nuclear development']
            },
            {
                'url': 'https://www.google.com/alerts/feeds/05477018627257484545/3724317091985668760',
                'name': 'Google Alert: SBTi',
                'keywords': ['sbti', 'science based targets initiative', 'science based targets', 'climate targets', 'net zero targets', 'carbon targets', 'emissions targets', 'climate science', 'corporate climate action', 'climate commitments', 'sustainability targets', 'climate goals', 'carbon reduction targets', 'climate action']
            },
            {
                'url': 'https://www.google.com/alerts/feeds/05477018627257484545/14074399320458355525',
                'name': 'Google Alert: OBBBA Renewables',
                'keywords': ['obbba', 'renewables', 'renewable energy', 'clean energy', 'sustainable energy', 'green energy', 'solar energy', 'wind energy', 'renewable power', 'clean power', 'sustainable power', 'renewable technology', 'energy transition', 'renewable development']
            },
            {
                'url': 'https://www.google.com/alerts/feeds/05477018627257484545/14810798000819807729',
                'name': 'Google Alert: NYISO',
                'keywords': ['nyiso', 'new york independent system operator', 'new york energy market', 'new york grid', 'new york electricity', 'new york power market', 'new york energy trading', 'new york grid operator', 'new york energy regulation', 'new york power grid', 'new york energy policy', 'northeast energy market']
            },
            {
                'url': 'https://www.google.com/alerts/feeds/05477018627257484545/6050091715561605058',
                'name': 'Google Alert: Europe Renewables',
                'keywords': ['europe renewable energy', 'europe renewables', 'eu renewable energy', 'europe solar', 'europe wind', 'europe clean energy', 'europe green energy', 'europe sustainable energy', 'europe renewable projects', 'europe energy transition', 'europe renewable development', 'europe renewable infrastructure', 'europe offshore wind', 'europe geothermal']
            },
            {
                'url': 'https://www.google.com/alerts/feeds/05477018627257484545/11867778498017191867',
                'name': 'Google Alert: FERC',
                'keywords': ['ferc', 'federal energy regulatory commission', 'energy regulation', 'energy policy', 'energy markets', 'energy infrastructure', 'energy transmission', 'energy storage', 'energy grid', 'energy reliability', 'energy security', 'energy trading', 'energy rates', 'energy tariffs', 'energy compliance']
            },
            {
                'url': 'https://www.google.com/alerts/feeds/05477018627257484545/6361645880654662282',
                'name': 'Google Alert: MISO',
                'keywords': ['miso', 'midcontinent independent system operator', 'miso grid', 'midwest energy market', 'midwest grid', 'midwest electricity', 'midwest power market', 'midwest energy trading', 'midwest grid operator', 'midwest energy regulation', 'midwest power grid', 'midwest energy policy', 'central energy market']
            },
            {
                'url': 'https://www.google.com/alerts/feeds/05477018627257484545/2971273721395665533',
                'name': 'Google Alert: Natural Gas',
                'keywords': ['natural gas', 'gas production', 'gas prices', 'gas markets', 'gas infrastructure', 'gas pipelines', 'gas storage', 'gas exports', 'gas imports', 'gas power plants', 'gas generation', 'gas supply', 'gas demand', 'gas trading', 'gas reserves']
            },
            {
                'url': 'https://www.google.com/alerts/feeds/05477018627257484545/590774740641410839',
                'name': 'Google Alert: PJM',
                'keywords': ['pjm', 'pjm interconnection', 'pjm grid', 'mid-atlantic energy market', 'mid-atlantic grid', 'mid-atlantic electricity', 'mid-atlantic power market', 'mid-atlantic energy trading', 'mid-atlantic grid operator', 'mid-atlantic energy regulation', 'mid-atlantic power grid', 'mid-atlantic energy policy', 'eastern energy market']
            }
        ]
        
        # Keywords for categorizing articles
        self.category_keywords = {
            'renewable': ['renewable', 'solar', 'wind', 'clean energy', 'green energy', 'sustainable energy'],
            'technology': ['technology', 'innovation', 'digital', 'ai', 'artificial intelligence', 'machine learning', 'automation'],
            'rto': ['rto', 'iso', 'grid operator', 'caiso', 'ercot', 'pjm', 'miso', 'nyiso', 'ferc', 'transmission'],
            'datacenters': ['data center', 'datacenter', 'server', 'cloud computing', 'digital infrastructure'],
            'esg': ['esg', 'environmental', 'social', 'governance', 'sustainability', 'corporate responsibility']
        }
        
        # Keywords for filtering out irrelevant content
        self.off_topic_keywords = ['sports', 'entertainment', 'celebrity', 'gossip', 'movie', 'music', 'game']
        
        # Store all articles
        self.all_articles = []
        
        # HTTP session with browser-like headers to reduce feed blocks
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
            'Accept': 'application/rss+xml, application/atom+xml, application/xml;q=0.9, text/xml;q=0.8, */*;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
        })

    def fetch_feed(self, url, feed_name):
        """Fetch and parse RSS/Atom feed with robust handling and diagnostics"""
        try:
            print(f"📡 Fetching {feed_name}...")

            # Fetch via requests with headers to avoid being blocked
            resp = self.session.get(url, timeout=20, allow_redirects=True)
            status = resp.status_code
            ctype = resp.headers.get('Content-Type', '')
            if status != 200:
                print(f"❌ HTTP {status} for {feed_name} ({url})")
                return []

            # Parse bytes explicitly
            feed = feedparser.parse(resp.content)
            
            # Diagnostics
            if getattr(feed, 'bozo', False):
                bozo_exc = getattr(feed, 'bozo_exception', None)
                print(f"⚠️  Parse issue for {feed_name} | content-type={ctype} | reason={bozo_exc}")
                sample = resp.text[:200].replace('\n', ' ')
                if 'text/html' in ctype.lower() or '<html' in sample.lower():
                    print("ℹ️  Received HTML instead of RSS; feed may require auth/cookies or is blocked.")
            
            articles = []
            for entry in feed.entries:
                # Skip entries without required fields
                if not all(key in entry for key in ['title', 'link', 'published']):
                    continue
                
                # Parse publication date
                try:
                    # Feedparser returns struct_time in UTC when tz provided; make it aware
                    pub_date_utc = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
                except Exception:
                    pub_date_utc = datetime.now(timezone.utc)
                
                # Skip articles older than 7 days or future dates (compare in UTC)
                now_utc = datetime.now(timezone.utc)
                if pub_date_utc < now_utc - timedelta(days=7) or pub_date_utc > now_utc:
                    continue
                
                article = {
                    'title': entry.title,
                    'link': entry.link,
                    'description': entry.get('summary', ''),
                    # Store pubDate as RFC 2822 in US Eastern time
                    'pubDate': format_datetime(pub_date_utc.astimezone(ZoneInfo('America/New_York'))),
                    'source': feed_name,
                    'categories': []
                }
                
                # Categorize article
                article['categories'] = self.categorize_article(article)
                
                # Check if article is relevant
                if self.is_relevant(article):
                    articles.append(article)
            
            print(f"✅ {feed_name}: {len(articles)} relevant articles")
            return articles
            
        except Exception as e:
            print(f"❌ Error fetching {feed_name}: {e}")
            return []

    def categorize_article(self, article):
        """Categorize article based on keywords"""
        categories = []
        text = f"{article['title']} {article['description']}".lower()
        
        for category, keywords in self.category_keywords.items():
            if any(keyword in text for keyword in keywords):
                categories.append(category)
        
        return categories

    def is_relevant(self, article):
        """Check if article is relevant (not off-topic)"""
        text = f"{article['title']} {article['description']}".lower()
        
        # Check for off-topic keywords
        if any(keyword in text for keyword in self.off_topic_keywords):
            return False
        
        return True

    def is_duplicate(self, article1, article2):
        """Check if two articles are duplicates based on title similarity and URL"""
        # Check if URLs are the same (exact match)
        if article1['link'] == article2['link']:
            return True
        
        # Check title similarity
        title1 = article1['title'].lower()
        title2 = article2['title'].lower()
        
        # Skip very short titles
        if len(title1) < 20 or len(title2) < 20:
            return False
        
        # Calculate word overlap
        words1 = set(title1.split())
        words2 = set(title2.split())
        
        if len(words1) < 3 or len(words2) < 3:
            return False
        
        overlap = len(words1.intersection(words2))
        total_words = len(words1.union(words2))
        
        if total_words == 0:
            return False
        
        similarity = overlap / total_words
        
        # Consider duplicate if similarity > 70%
        return similarity > 0.7

    def remove_duplicates(self, articles):
        """Remove duplicate articles"""
        unique_articles = []
        duplicates_removed = 0
        
        for article in articles:
            is_duplicate = False
            for existing in unique_articles:
                if self.is_duplicate(article, existing):
                    is_duplicate = True
                    duplicates_removed += 1
                    break
            
            if not is_duplicate:
                unique_articles.append(article)
        
        print(f"🔄 Removed {duplicates_removed} duplicate articles")
        return unique_articles

    def create_feed(self):
        """Create RSS feed from all articles"""
        print("\n🔄 Processing articles...")
        
        # Fetch from Google Alerts
        for feed in self.google_alerts_feeds:
            articles = self.fetch_feed(feed['url'], feed['name'])
            self.all_articles.extend(articles)
        
        # Remove duplicates
        self.all_articles = self.remove_duplicates(self.all_articles)
        
        # Sort by date (newest first) - convert string dates to datetime objects for proper sorting
        def parse_date(date_str):
            try:
                return parsedate_to_datetime(date_str)
            except Exception:
                return datetime.now(timezone.utc)
        
        self.all_articles.sort(key=lambda x: parse_date(x['pubDate']), reverse=True)
        
        print(f"\n📊 Total articles after processing: {len(self.all_articles)}")
        
        # Generate RSS feed
        self.generate_rss(self.all_articles, 'feed.xml')
        
        # Export to CSV
        csv_file = self.export_to_csv(self.all_articles)
        
        # Generate static HTML page
        self.generate_static_html(self.all_articles)
        
        return self.all_articles

    def generate_rss(self, articles, output_file='feed.xml'):
        """Generate RSS XML feed"""
        # Create RSS structure
        rss = ET.Element('rss', version='2.0')
        channel = ET.SubElement(rss, 'channel')
        
        # Channel metadata
        ET.SubElement(channel, 'title').text = 'Sustain74 ESG News Feed'
        ET.SubElement(channel, 'description').text = 'Latest ESG and sustainability news curated by Sustain74'
        ET.SubElement(channel, 'link').text = 'https://www.sustain74.com'
        ET.SubElement(channel, 'language').text = 'en-us'
        # Use US Eastern for lastBuildDate in RFC 2822 format
        eastern_now = datetime.now(timezone.utc).astimezone(ZoneInfo('America/New_York'))
        ET.SubElement(channel, 'lastBuildDate').text = format_datetime(eastern_now)
        
        # Add items
        for article in articles:
            item = ET.SubElement(channel, 'item')
            ET.SubElement(item, 'title').text = article['title']
            ET.SubElement(item, 'description').text = article['description']
            ET.SubElement(item, 'link').text = article['link']
            ET.SubElement(item, 'pubDate').text = article['pubDate']
            ET.SubElement(item, 'source').text = article['source']
            
            if article['categories']:
                ET.SubElement(item, 'categories').text = ', '.join(article['categories'])
        
        # Write to file
        tree = ET.ElementTree(rss)
        tree.write(output_file, encoding='utf-8', xml_declaration=True)
        print(f"✅ Successfully created RSS feed with {len(articles)} articles")
        print(f"📄 Feed saved as: {output_file}")
        print(f"🌐 Add this to your website at: https://www.sustain74.com/{output_file}")

    def export_to_csv(self, articles, output_file=None):
        """Export articles to CSV with tags"""
        # If no output file specified, save to Google Drive folder (if it exists) or current directory
        if output_file is None:
            google_drive_path = "/Users/michaelbarry/Library/CloudStorage/GoogleDrive-mickeybarry@gmail.com/My Drive/NewsFeed"
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # Check if Google Drive path exists (local development)
            if os.path.exists(google_drive_path):
                output_file = os.path.join(google_drive_path, f"ESG_Stories_{timestamp}.csv")
            else:
                # Fallback for GitHub Actions or other environments
                output_file = f"ESG_Stories_{timestamp}.csv"
        
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Date', 'Title', 'Description', 'Link', 'Source', 'Categories', 'Tags']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for article in articles:
                # Format date for CSV
                try:
                    pub_dt = parsedate_to_datetime(article['pubDate'])
                    # Convert to US Eastern for CSV output (without tz suffix for brevity)
                    pub_dt_eastern = pub_dt.astimezone(ZoneInfo('America/New_York'))
                    formatted_date = pub_dt_eastern.strftime('%Y-%m-%d %H:%M:%S')
                except Exception:
                    formatted_date = article['pubDate']
                
                # Clean up description (remove HTML tags)
                clean_description = re.sub(r'<[^>]+>', '', article['description'])
                
                writer.writerow({
                    'Date': formatted_date,
                    'Title': article['title'],
                    'Description': clean_description,
                    'Link': article['link'],
                    'Source': article['source'],
                    'Categories': ', '.join(article.get('categories', [])),
                    'Tags': ', '.join(article.get('categories', []))  # Same as categories for now
                })
        
        print(f"📊 CSV exported with {len(articles)} stories: {output_file}")
        return output_file

    def extract_real_website(self, google_url):
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

    def clean_source_name(self, source):
        """Clean up the source name for display"""
        return source.replace('Google Alert: ', '')

    def format_date(self, date_str):
        """Format the date for display"""
        try:
            # Parse the date string
            dt = datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S GMT')
            return dt.strftime('%b %d, %Y')
        except:
            return date_str

    def clean_title(self, title):
        """Clean HTML entities from title"""
        # Remove HTML tags
        title = re.sub(r'<[^>]+>', '', title)
        # Decode HTML entities
        title = title.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
        title = title.replace('&quot;', '"').replace('&#39;', "'")
        return title

    # generate_tldr removed (AI summary disabled)

    def generate_static_html(self, articles):
        """Generate static HTML page with embedded news content"""
        print("\n🌐 Generating static HTML page...")
        
        # Sort by date (newest first) - convert string dates to datetime objects for proper sorting
        def parse_date(date_str):
            try:
                return parsedate_to_datetime(date_str)
            except Exception:
                return datetime.now(timezone.utc)
        
        articles_sorted = sorted(articles, key=lambda x: parse_date(x['pubDate']), reverse=True)
        
        # AI summary generation removed
        
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
        
        /* AI summary styles removed */
        
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
        
        .category-tag {{
            cursor: pointer;
            transition: all 0.2s ease;
            user-select: none;
        }}
        
        .category-tag:hover {{
            background: #1976d2 !important;
            color: white !important;
            transform: scale(1.05);
            box-shadow: 0 2px 8px rgba(25, 118, 210, 0.3);
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
    <link rel="stylesheet" href="css/style.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
</head>
<body>
    <header class="site-header">
        <nav class="nav">
            <a href="index.html" class="logo"><img src="assets/sustain74_logo.png" alt="Sustain74 Logo"></a>
            <button class="nav-toggle" aria-label="toggle navigation">☰</button>
            <ul class="nav-list">
                <li><a href="index.html">Home</a></li>
                <li><a href="michael-barry.html">Our Story</a></li>
                <li><a href="services.html">Our Solutions</a></li>
                <li><a href="sample-engagements.html">Sample Engagements</a></li>
                <li><a href="blog/index.html">Blog</a></li>
                <li><a href="esg-news-static.html" class="active">ESG News</a></li>
                <li><a href="contact.html">Contact</a></li>
            </ul>
        </nav>
    </header>

    <div class="container">
        <div class="header">
            <h1>Sustain74 ESG News Feed</h1>
            <p>Latest ESG and sustainability news curated by Sustain74</p>
            <div class="stats">
                <span>📊 {len(articles_sorted)} Articles</span>
                <span>🕒 Last Updated: {datetime.now(timezone.utc).astimezone(ZoneInfo('America/New_York')).strftime('%B %d, %Y at %I:%M %p %Z')}</span>
            </div>
        </div>
        
        <div class="filter-section">
            <h3>🔍 Filter by Category <span style="font-size: 14px; color: #666; font-weight: normal;">(Click multiple to combine)</span></h3>
            <div class="category-filters" id="categoryFilters">
                <!-- Category buttons will be generated by JavaScript -->
            </div>
            <div class="filter-controls">
                <button id="showAllBtn" style="background: #2c5aa0; color: white; border: none; padding: 10px 20px; border-radius: 6px; cursor: pointer; font-size: 16px; display: none;">
                    🔄 Show All Categories
                </button>
            </div>
        </div>
        
        <div class="news-grid">
"""
        
        # Add each article
        for article in articles_sorted:
            website = self.extract_real_website(article['link'])
            category = self.clean_source_name(article['source'])
            html_content += f"""
            <div class="news-card" data-category="{category}">
                <div class="news-meta">
                    <span class="source category-tag">{category}</span>
                    <span class="date">{self.format_date(article['pubDate'])}</span>
                </div>
                <h3><a href="{article['link']}" target="_blank" rel="noopener noreferrer">{self.clean_title(article['title'])}</a></h3>
                <div class="website">{website}</div>
            </div>
"""
        
        html_content += """
        </div>
    </div>
    <script src="js/main.js"></script>
</body>
</html>
"""
        
        # Write to file
        with open('esg-news-static.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ Generated static news page with {len(articles_sorted)} articles")
        print("📄 File: esg-news-static.html")

    def send_csv_email(self, csv_file, recipient_email='michael@sustain74.com'):
        """Send CSV file via email"""
        try:
            # Email configuration
            sender_email = "noreply@sustain74.com"  # You may need to update this
            subject = f"ESG Stories Report - {datetime.now().strftime('%Y-%m-%d')}"
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = recipient_email
            msg['Subject'] = subject
            
            # Email body
            body = f"""
            Hi Michael,
            
            Here's your daily ESG stories report with {len(self.all_articles)} articles.
            
            The CSV file contains:
            - Date and time of publication
            - Article title and description
            - Source and link
            - Categories/tags assigned
            
            Best regards,
            Sustain74 RSS Aggregator
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Attach CSV file
            with open(csv_file, "rb") as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
            
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {os.path.basename(csv_file)}'
            )
            msg.attach(part)
            
            # Send email (this would need SMTP configuration)
            print(f"📧 CSV file ready to send to {recipient_email}")
            print(f"📎 Attached file: {csv_file}")
            print("Note: SMTP configuration required to actually send email")
            
            return True
            
        except Exception as e:
            print(f"❌ Error preparing email: {e}")
            return False

def main():
    """Main function to run the RSS aggregator"""
    print("🚀 Starting Sustain74 RSS Aggregator...")
    print("=" * 50)
    
    aggregator = RSSAggregator()
    
    # Create feed and get articles
    articles = aggregator.create_feed()
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 SUMMARY")
    print("=" * 50)
    print(f"✅ Total articles processed: {len(articles)}")
    print(f"📄 RSS Feed: feed.xml")
    print(f"🌐 Static Page: esg-news-static.html")
    print(f"📊 CSV Export: Google Drive ESG News folder")
    print(f"\n✅ All done! One command completed everything!")
    print(f"🌐 View your news at: https://www.sustain74.com/esg-news-static.html")

if __name__ == "__main__":
    main()
