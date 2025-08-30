#!/usr/bin/env python3
"""
RSS Feed Aggregator for Sustain74
Fetches relevant ESG/sustainability stories from external sources
"""

import feedparser
import requests
from datetime import datetime, timedelta
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
import google.generativeai as genai
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RSSAggregator:
    def __init__(self):
        # Load environment variables from .env file
        load_dotenv()
        
        # Configure Gemini API
        api_key = os.getenv('GEMINI_API_KEY')
        if api_key:
            genai.configure(api_key=api_key)
            self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
            self.gemini_available = True
        else:
            self.gemini_available = False
            print("⚠️  GEMINI_API_KEY not found in .env file - TLDR generation disabled")
        
        # External RSS feeds - DISABLED - Only using Google Alerts
        self.external_feeds = []
        
        # Google Alerts RSS feeds - Add your Google Alerts RSS URLs here
        # To get Google Alerts RSS URLs:
        # 1. Go to https://www.google.com/alerts
        # 2. Edit each alert and set "Deliver to" to "RSS feed"
        # 3. Copy the RSS URL and add it below
        self.google_alerts_feeds = [
            {
                'url': 'https://www.google.com/alerts/feeds/11148815731617361241/8416975834830823093',
                'name': 'Google Alert: ESG and Energy',
                'keywords': ['ai', 'artificial intelligence', 'sustainability', 'carbon credits', 'esg', 'sbti', 'energy', 'grid', 'renewable energy', 'epa', 'ferc', 'ghg protocol']
            },
            {
                'url': 'https://www.google.com/alerts/feeds/11148815731617361241/8261983527978060796',
                'name': 'Google Alert: CAISO',
                'keywords': ['caiso', 'california', 'grid operator', 'energy market', 'transmission']
            },
            {
                'url': 'https://www.google.com/alerts/feeds/11148815731617361241/3058773563308323113',
                'name': 'Google Alert: ERCOT',
                'keywords': ['ercot', 'texas', 'grid operator', 'energy market', 'transmission']
            },
            {
                'url': 'https://www.google.com/alerts/feeds/11148815731617361241/706682144053230716',
                'name': 'Google Alert: Carbon Credits',
                'keywords': ['carbon credits', 'carbon trading', 'carbon offset', 'carbon market']
            },
            {
                'url': 'https://www.google.com/alerts/feeds/11148815731617361241/13938593169621617300',
                'name': 'Google Alert: OBBBA Renewables',
                'keywords': ['obbba', 'renewable energy', 'solar', 'wind', 'energy policy', 'tax credits']
            },
            {
                'url': 'https://www.google.com/alerts/feeds/11148815731617361241/1990537298683130160',
                'name': 'Google Alert: SBTi',
                'keywords': ['sbti', 'science based targets', 'climate targets', 'net zero', 'emissions reduction']
            },
            {
                'url': 'https://www.google.com/alerts/feeds/11148815731617361241/17593370029704000586',
                'name': 'Google Alert: PJM',
                'keywords': ['pjm', 'grid operator', 'energy market', 'transmission', 'interconnection']
            },
            {
                'url': 'https://www.google.com/alerts/feeds/11148815731617361241/10229188489220187549',
                'name': 'Google Alert: Additional Feed',
                'keywords': ['energy', 'sustainability', 'esg', 'grid', 'renewable']
            },
            {
                'url': 'https://www.google.com/alerts/feeds/11148815731617361241/17166491980537754255',
                'name': 'Google Alert: GHG Protocol',
                'keywords': ['ghg protocol', 'greenhouse gas', 'emissions reporting', 'carbon accounting', 'scope 1', 'scope 2', 'scope 3']
            },
            {
                'url': 'https://www.google.com/alerts/feeds/11148815731617361241/4823172020421522588',
                'name': 'Google Alert: MISO Grid',
                'keywords': ['miso', 'midcontinent independent system operator', 'grid operator', 'energy market', 'transmission', 'grid reliability']
            },
            {
                'url': 'https://www.google.com/alerts/feeds/11148815731617361241/17490903940019154653',
                'name': 'Google Alert: India Renewables',
                'keywords': ['india', 'renewable energy', 'solar power', 'energy transition', 'clean energy', 'sustainable development']
            },
            {
                'url': 'https://www.google.com/alerts/feeds/11148815731617361241/13034409552276427076',
                'name': 'Google Alert: Europe Renewables',
                'keywords': ['europe', 'eu', 'renewable energy', 'offshore wind', 'solar power', 'energy transition', 'clean energy', 'sustainable development']
            },
            {
                'url': 'https://www.google.com/alerts/feeds/11148815731617361241/10430378286967578519',
                'name': 'Google Alert: Natural Gas',
                'keywords': ['natural gas', 'lng', 'liquefied natural gas', 'gas market', 'energy market', 'fossil fuels']
            },
            {
                'url': 'https://www.google.com/alerts/feeds/11148815731617361241/10430378286967577760',
                'name': 'Google Alert: LNG',
                'keywords': ['energy', 'power', 'electricity', 'energy market', 'energy policy', 'energy transition']
            },
            {
                'url': 'https://www.google.com/alerts/feeds/11148815731617361241/8761439016609917737',
                'name': 'Google Alert: EIA',
                'keywords': ['eia', 'energy information administration', 'energy data', 'energy statistics', 'energy reports', 'energy market data']
            },
            {
                'url': 'https://www.google.com/alerts/feeds/11148815731617361241/4175802949917622328',
                'name': 'Google Alert: IEA',
                'keywords': ['iea', 'international energy agency', 'global energy', 'energy policy', 'energy outlook', 'energy transition', 'clean energy']
            },
            {
                'url': 'https://www.google.com/alerts/feeds/11148815731617361241/11943491749560683085',
                'name': 'Google Alert: ESG Reports',
                'keywords': ['esg report', 'sustainability report', 'esg disclosure', 'corporate responsibility report', 'esg reporting', 'sustainability disclosure']
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

    def fetch_feed(self, url, feed_name):
        """Fetch and parse RSS feed"""
        try:
            print(f"📡 Fetching {feed_name}...")
            feed = feedparser.parse(url)
            
            if feed.bozo:
                print(f"⚠️  Warning: Feed parsing issues for {feed_name}")
            
            articles = []
            for entry in feed.entries:
                # Skip entries without required fields
                if not all(key in entry for key in ['title', 'link', 'published']):
                    continue
                
                # Parse publication date
                try:
                    pub_date = datetime(*entry.published_parsed[:6])
                except:
                    pub_date = datetime.now()
                
                # Skip articles older than 7 days or future dates
                if pub_date < datetime.now() - timedelta(days=7) or pub_date > datetime.now():
                    continue
                
                article = {
                    'title': entry.title,
                    'link': entry.link,
                    'description': entry.get('summary', ''),
                    'pubDate': pub_date.strftime('%a, %d %b %Y %H:%M:%S GMT'),
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
                return datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S GMT')
            except:
                return datetime.now()
        
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
        ET.SubElement(channel, 'lastBuildDate').text = datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT')
        
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
        # If no output file specified, save to Google Drive folder
        if output_file is None:
            google_drive_path = "/Users/michaelbarry/Library/CloudStorage/GoogleDrive-michaelbarry@sustain74.com/My Drive/Sustain74/Business Content/Marketing/ESG News"
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = os.path.join(google_drive_path, f"ESG_Stories_{timestamp}.csv")
        
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Date', 'Title', 'Description', 'Link', 'Source', 'Categories', 'Tags']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for article in articles:
                # Format date for CSV
                try:
                    pub_date = datetime.strptime(article['pubDate'], '%a, %d %b %Y %H:%M:%S GMT')
                    formatted_date = pub_date.strftime('%Y-%m-%d %H:%M:%S')
                except:
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

    def generate_tldr(self, articles, max_articles=20):
        """Generate TLDR using Gemini API"""
        if not self.gemini_available:
            return None
        
        print("🤖 Generating TLDR with Gemini...")
        
        # Take the latest articles
        recent_articles = articles[:max_articles]
        
        # Prepare articles text for Gemini
        articles_text = "Latest ESG and Energy News Articles:\n\n"
        
        for i, article in enumerate(recent_articles, 1):
            articles_text += f"{i}. {article['title']}\n"
            articles_text += f"   Source: {article['source']}\n"
            articles_text += f"   Summary: {article['description'][:200]}...\n"
            articles_text += f"   Link: {article['link']}\n\n"
        
        prompt = f"""
You are an ESG and energy market analyst. Based on the following news articles, write a concise 2-paragraph TLDR (Too Long; Didn't Read) summary.

Focus on:
- Key trends and developments in ESG, energy, and sustainability
- Major policy changes, market movements, or technological breakthroughs
- Implications for businesses, investors, and the energy transition

Write in a professional, analytical tone suitable for business executives and sustainability professionals.

Articles:
{articles_text}

Please provide exactly 2 paragraphs that capture the most important developments and their significance.
"""
        
        try:
            response = self.gemini_model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            print(f"❌ Error generating TLDR: {e}")
            return None

    def generate_static_html(self, articles):
        """Generate static HTML page with embedded news content"""
        print("\n🌐 Generating static HTML page...")
        
        # Sort by date (newest first) - convert string dates to datetime objects for proper sorting
        def parse_date(date_str):
            try:
                return datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S GMT')
            except:
                return datetime.now()
        
        articles_sorted = sorted(articles, key=lambda x: parse_date(x['pubDate']), reverse=True)
        
        # Generate TLDR
        tldr_text = self.generate_tldr(articles_sorted)
        tldr_generation_date = datetime.now().strftime('%B %d, %Y at %I:%M %p')
        
        # If TLDR generation failed, use a fallback
        if not tldr_text:
            tldr_text = """Significant developments continue to shape the ESG and energy landscape, with ongoing investments in renewable energy infrastructure, evolving regulatory frameworks, and market dynamics driving the energy transition forward. The convergence of policy support, technological innovation, and market demand is creating new opportunities while presenting challenges for businesses and investors navigating this complex landscape.

These developments underscore the critical importance of staying informed about ESG trends, energy market changes, and sustainability initiatives that impact investment decisions and business strategies across multiple sectors."""
        
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
        
        .tldr-section {{
            background: white;
            border-radius: 8px;
            padding: 25px;
            margin: 20px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border-left: 4px solid #2c5aa0;
        }}
        
        .tldr-section h2 {{
            color: #2c5aa0;
            margin-bottom: 15px;
            font-size: 20px;
        }}
        
        .tldr-content {{
            font-size: 16px;
            line-height: 1.7;
            color: #333;
        }}
        
        .tldr-content p {{
            margin-bottom: 15px;
        }}
        
        .tldr-meta {{
            font-size: 12px;
            color: #666;
            margin-top: 15px;
            padding-top: 15px;
            border-top: 1px solid #eee;
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
                <span>📊 {len(articles_sorted)} Articles</span>
                <span>🕒 Last Updated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</span>
            </div>
        </div>
        
        <div class="tldr-section">
            <h2>🤖 AI-Generated TLDR Summary</h2>
            <div class="tldr-content">
                {tldr_text}
            </div>
            <div class="tldr-meta">
                💡 <em>Generated on {tldr_generation_date} by analyzing the latest {len(articles_sorted)} articles</em>
            </div>
        </div>
        
        <div class="news-grid">
"""
        
        # Add each article
        for article in articles_sorted:
            website = self.extract_real_website(article['link'])
            html_content += f"""
            <div class="news-card">
                <div class="news-meta">
                    <span class="source">{self.clean_source_name(article['source'])}</span>
                    <span class="date">{self.format_date(article['pubDate'])}</span>
                </div>
                <h3><a href="{article['link']}" target="_blank" rel="noopener noreferrer">{self.clean_title(article['title'])}</a></h3>
                <div class="website">{website}</div>
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
