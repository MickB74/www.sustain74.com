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

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RSSAggregator:
    def __init__(self):
        # External RSS feeds focused on ESG/sustainability
        self.external_feeds = [
            {
                'url': 'https://www.climatechangenews.com/feed/',
                'name': 'Climate Change News',
                'keywords': ['climate', 'sustainability', 'environment']
            },
            {
                'url': 'https://www.esgtoday.com/feed/',
                'name': 'ESG Today',
                'keywords': ['esg', 'sustainability', 'governance']
            },
            {
                'url': 'https://www.corporateknights.com/feed/',
                'name': 'Corporate Knights',
                'keywords': ['sustainability', 'esg', 'corporate responsibility']
            },
            {
                'url': 'https://www.datacenterknowledge.com/rss.xml',
                'name': 'Data Center Knowledge',
                'keywords': ['data center', 'data centres', 'sustainability', 'energy efficiency', 'green data center', 'carbon footprint']
            },
            {
                'url': 'https://www.techrepublic.com/rssfeeds/topic/sustainability/',
                'name': 'TechRepublic Sustainability',
                'keywords': ['sustainability', 'green tech', 'energy efficiency', 'data center', 'esg']
            },
            {
                'url': 'https://feeds.feedburner.com/EnvironmentalLeader',
                'name': 'Environmental Leader',
                'keywords': ['environmental', 'sustainability', 'esg', 'energy efficiency']
            },
            {
                'url': 'https://www.energymanagertoday.com/feed/',
                'name': 'Energy Manager Today',
                'keywords': ['energy', 'energy management', 'sustainability', 'energy efficiency']
            },
            {
                'url': 'https://www.renewableenergyworld.com/feed/',
                'name': 'Renewable Energy World',
                'keywords': ['renewable energy', 'solar', 'wind', 'clean energy', 'sustainability']
            },
            {
                'url': 'https://www.utilitydive.com/rss/',
                'name': 'Utility Dive',
                'keywords': ['utility', 'energy', 'renewable', 'sustainability', 'grid']
            },
            {
                'url': 'https://www.greentechmedia.com/rss',
                'name': 'Greentech Media',
                'keywords': ['sustainability', 'renewable', 'clean energy', 'esg']
            },
            {
                'url': 'https://www.cleanenergywire.org/rss.xml',
                'name': 'Clean Energy Wire',
                'keywords': ['clean energy', 'renewable', 'sustainability', 'energy transition']
            },
            {
                'url': 'https://www.energycentral.com/rss.xml',
                'name': 'Energy Central',
                'keywords': ['energy', 'utility', 'renewable', 'sustainability']
            },
            {
                'url': 'https://www.solarpowerworldonline.com/feed/',
                'name': 'Solar Power World',
                'keywords': ['solar', 'renewable energy', 'clean energy', 'sustainability']
            },
            {
                'url': 'https://www.windpowerengineering.com/feed/',
                'name': 'Wind Power Engineering',
                'keywords': ['wind power', 'renewable energy', 'clean energy', 'sustainability']
            },
            {
                'url': 'https://www.energynewsnetwork.org/feed/',
                'name': 'Energy News Network',
                'keywords': ['energy', 'renewable', 'sustainability', 'clean energy']
            },
            {
                'url': 'https://www.greenbiz.com/feed',
                'name': 'GreenBiz',
                'keywords': ['sustainability', 'esg', 'green business', 'climate']
            },
            # New sources for Technology & Innovation
            {
                'url': 'https://www.venturebeat.com/category/ai/feed/',
                'name': 'VentureBeat AI',
                'keywords': ['ai', 'artificial intelligence', 'technology', 'innovation', 'sustainability']
            },
            {
                'url': 'https://www.techcrunch.com/tag/artificial-intelligence/feed/',
                'name': 'TechCrunch AI',
                'keywords': ['ai', 'artificial intelligence', 'technology', 'innovation']
            },
            {
                'url': 'https://www.zdnet.com/news/rss.xml',
                'name': 'ZDNet',
                'keywords': ['technology', 'ai', 'artificial intelligence', 'innovation', 'sustainability']
            },
            {
                'url': 'https://www.axios.com/feed.rss',
                'name': 'Axios',
                'keywords': ['technology', 'ai', 'sustainability', 'esg', 'innovation']
            },
            # New sources for Supply Chain
            {
                'url': 'https://www.supplychaindive.com/rss/',
                'name': 'Supply Chain Dive',
                'keywords': ['supply chain', 'logistics', 'manufacturing', 'sustainability']
            },
            {
                'url': 'https://www.supplychainbrain.com/rss/',
                'name': 'Supply Chain Brain',
                'keywords': ['supply chain', 'logistics', 'manufacturing', 'sustainability']
            },
            {
                'url': 'https://www.industryweek.com/rss.xml',
                'name': 'Industry Week',
                'keywords': ['manufacturing', 'industrial', 'supply chain', 'sustainability']
            },
            {
                'url': 'https://www.manufacturingtomorrow.com/rss/',
                'name': 'Manufacturing Tomorrow',
                'keywords': ['manufacturing', 'industrial', 'technology', 'sustainability']
            },
            # Additional ESG and sustainability sources
            {
                'url': 'https://www.triplepundit.com/feed/',
                'name': 'TriplePundit',
                'keywords': ['sustainability', 'esg', 'social responsibility', 'supply chain']
            },
            {
                'url': 'https://www.sustainablebrands.com/feed/',
                'name': 'Sustainable Brands',
                'keywords': ['sustainability', 'esg', 'brands', 'supply chain']
            },
            {
                'url': 'https://www.edie.net/rss/',
                'name': 'Edie',
                'keywords': ['sustainability', 'esg', 'environmental', 'technology']
            }
        ]
        
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
            }
        ]
        
        # Industry-related keywords for filtering
        self.industry_keywords = [
            'esg', 'environmental', 'social', 'governance',
            'sustainability', 'sustainable', 'climate', 'carbon',
            'renewable', 'green energy', 'clean energy',
            'net zero', 'carbon neutral', 'emissions',
            'biodiversity', 'circular economy', 'scope 3',
            'sbti', 'science based targets', 'cdp',
            'tcfd', 'sasb', 'gri', 'ungc',
            'carbon credits', 'carbon offset', 'carbon trading',
            'data center', 'data centres', 'server farm',
            'renewable energy', 'solar', 'wind power', 'clean energy',
            # RTO and grid operators
            'nyiso', 'caiso', 'pjm', 'ercot', 'ferc', 'rto', 'iso',
            'grid operator', 'transmission', 'electricity market',
            'power market', 'energy market', 'grid modernization',
            'smart grid', 'grid reliability', 'interconnection'
        ]

    def fetch_feed(self, feed_url, timeout=10):
        """Fetch and parse an RSS feed"""
        try:
            logger.info(f"Fetching feed: {feed_url}")
            response = requests.get(feed_url, timeout=timeout)
            response.raise_for_status()
            feed = feedparser.parse(response.content)
            return feed
        except Exception as e:
            logger.error(f"Error fetching {feed_url}: {e}")
            return None

    def is_relevant(self, title, description):
        """Check if an article is relevant to industry news"""
        text = (title + ' ' + description).lower()
        
        # Check for industry keywords
        for keyword in self.industry_keywords:
            if keyword.lower() in text:
                return True
        return False

    def categorize_article(self, title, description):
        """Categorize article based on keywords"""
        text = (title + ' ' + description).lower()
        categories = []
        
        # Carbon Credits
        if any(keyword in text for keyword in ['carbon credit', 'carbon offset', 'carbon trading', 'carbon market']):
            categories.append('carbon')
        
        # Renewable Energy
        if any(keyword in text for keyword in ['renewable energy', 'solar', 'wind power', 'clean energy', 'green energy']):
            categories.append('renewable')
        
        # Data Centers
        if any(keyword in text for keyword in ['data center', 'data centre', 'server farm', 'cloud computing']):
            categories.append('datacenters')
        
        # ESG
        if any(keyword in text for keyword in ['esg', 'environmental social governance', 'sustainability']):
            categories.append('esg')
        
        # Technology & Innovation
        if any(keyword in text for keyword in ['ai', 'artificial intelligence', 'innovation', 'technology', 'digital', 'clean tech', 'smart', 'automation', 'machine learning']):
            categories.append('technology')
        
        # Supply Chain
        if any(keyword in text for keyword in ['supply chain', 'manufacturing', 'factory', 'industrial', 'scope 3', 'value chain', 'logistics', 'procurement']):
            categories.append('supplychain')
        
        # RTO/Grid
        if any(keyword in text for keyword in ['nyiso', 'caiso', 'pjm', 'ercot', 'ferc', 'rto', 'iso', 'grid operator', 'transmission']):
            categories.append('rto')
        
        return categories

    def extract_articles(self, feed, source_name, keywords):
        """Extract relevant articles from a feed"""
        articles = []
        
        if not feed or not feed.entries:
            return articles
            
        # For Google Alerts, take more entries and skip filtering
        max_entries = 100 if "Google Alert" in source_name else 20
        skip_filtering = "Google Alert" in source_name
            
        for entry in feed.entries[:max_entries]:
            title = entry.get('title', '')
            description = entry.get('description', '') or entry.get('summary', '')
            
            # Clean HTML tags from description
            description = re.sub(r'<[^>]+>', '', description)
            
            # Check if article is relevant (skip for Google Alerts)
            if skip_filtering or self.is_relevant(title, description):
                # Parse date
                published = entry.get('published_parsed') or entry.get('updated_parsed')
                if published:
                    pub_date = datetime(*published[:6])
                else:
                    pub_date = datetime.now()
                
                # Only include articles from last 30 days and not future dates
                if datetime.now() - pub_date <= timedelta(days=30) and pub_date <= datetime.now():
                    # Categorize the article
                    categories = self.categorize_article(title, description)
                    
                    articles.append({
                        'title': title,
                        'description': description[:300] + '...' if len(description) > 300 else description,
                        'link': entry.get('link', ''),
                        'pubDate': pub_date.strftime('%a, %d %b %Y %H:%M:%S GMT'),
                        'pubDateObj': pub_date,  # Keep datetime object for sorting
                        'source': source_name,
                        'guid': entry.get('id', entry.get('link', '')),
                        'categories': categories
                    })
        
        return articles

    def generate_rss(self, articles, output_file='feed.xml'):
        """Generate RSS XML from articles"""
        rss = ET.Element('rss', version='2.0')
        channel = ET.SubElement(rss, 'channel')
        
        ET.SubElement(channel, 'title').text = 'Sustain74 ESG News Feed'
        ET.SubElement(channel, 'description').text = 'Latest ESG and sustainability news curated by Sustain74'
        ET.SubElement(channel, 'link').text = 'https://www.sustain74.com'
        ET.SubElement(channel, 'language').text = 'en-us'
        ET.SubElement(channel, 'lastBuildDate').text = datetime.now().strftime('%a, %d %b %Y %H:%M:%S %z')
        
        for article in articles:
            item = ET.SubElement(channel, 'item')
            ET.SubElement(item, 'title').text = article['title']
            ET.SubElement(item, 'description').text = article['description']
            ET.SubElement(item, 'link').text = article['link']
            ET.SubElement(item, 'pubDate').text = article['pubDate']
            ET.SubElement(item, 'source').text = article['source']
            # Add categories as comma-separated string
            if article.get('categories'):
                ET.SubElement(item, 'categories').text = ', '.join(article['categories'])
        
        tree = ET.ElementTree(rss)
        tree.write(output_file, encoding='utf-8', xml_declaration=True)
        print(f"✅ Successfully created RSS feed with {len(articles)} articles")
        print(f"📄 Feed saved as: {output_file}")
        print(f"🌐 Add this to your website at: https://www.sustain74.com/{output_file}")

    def export_to_csv(self, articles, output_file='esg_stories.csv'):
        """Export articles to CSV with tags"""
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Date', 'Title', 'Description', 'Link', 'Source', 'Categories', 'Tags']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for article in articles:
                # Format date for CSV
                try:
                    pub_date = datetime.strptime(article['pubDate'], '%a, %d %b %Y %H:%M:%S %z')
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

    def create_feed(self, output_file='feed.xml'):
        """Create the aggregated RSS feed"""
        self.all_articles = []
        
        # Fetch articles from external feeds
        for feed_config in self.external_feeds:
            feed = self.fetch_feed(feed_config['url'])
            if feed:
                articles = self.extract_articles(
                    feed, 
                    feed_config['name'], 
                    feed_config['keywords']
                )
                self.all_articles.extend(articles)
                logger.info(f"Found {len(articles)} relevant articles from {feed_config['name']}")
        
        # Fetch articles from Google Alerts feeds
        for feed_config in self.google_alerts_feeds:
            feed = self.fetch_feed(feed_config['url'])
            if feed:
                # Get all articles from Google Alerts without keyword filtering
                articles = self.extract_articles(
                    feed, 
                    feed_config['name'], 
                    []  # Empty keywords list to get all articles
                )
                self.all_articles.extend(articles)
                logger.info(f"Found {len(articles)} articles from {feed_config['name']}")
        
        # Sort articles by publication date (newest first)
        self.all_articles.sort(key=lambda x: x['pubDateObj'], reverse=True)
        
        # Generate RSS XML
        self.generate_rss(self.all_articles, output_file)
        
        logger.info(f"Created RSS feed with {len(self.all_articles)} articles: {output_file}")
        return len(self.all_articles)

def main():
    """Main function for testing"""
    print("\nSustain74 RSS Feed Aggregator")
    print("===================================")
    
    aggregator = RSSAggregator()
    aggregator.create_feed()
    
    # Export to CSV
    csv_file = aggregator.export_to_csv(aggregator.all_articles)
    
    # Prepare email (without sending - requires SMTP setup)
    aggregator.send_csv_email(csv_file)
    
    print(f"\n📊 Summary:")
    print(f"   - RSS Feed: feed.xml ({len(aggregator.all_articles)} articles)")
    print(f"   - CSV Export: {csv_file}")
    print(f"   - Email prepared for: michael@sustain74.com")
    print(f"\nTo enable email sending, configure SMTP settings in the script.")

if __name__ == "__main__":
    print("\nSustain74 RSS Feed Aggregator")
    print("===================================")
    
    aggregator = RSSAggregator()
    aggregator.create_feed()
    
    # Export to CSV
    csv_file = aggregator.export_to_csv(aggregator.all_articles)
    
    # Try to upload to Google Drive
    try:
        from drive_uploader import upload_to_drive
        print(f"\n📤 Attempting to upload to Google Drive...")
        file_id = upload_to_drive(csv_file)
        if file_id:
            print(f"✅ Successfully uploaded to Google Drive!")
        else:
            print(f"⚠️  Google Drive upload failed - CSV file saved locally: {csv_file}")
    except ImportError:
        print(f"⚠️  Google Drive uploader not available - CSV file saved locally: {csv_file}")
    except Exception as e:
        print(f"⚠️  Google Drive upload error: {e}")
        print(f"📄 CSV file saved locally: {csv_file}")
    
    print(f"\n📊 Summary:")
    print(f"   - RSS Feed: feed.xml ({len(aggregator.all_articles)} articles)")
    print(f"   - CSV Export: {csv_file}")
    print(f"   - Google Drive: Upload attempted")
