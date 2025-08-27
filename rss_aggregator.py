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
            }
        ]
        
        # Industry-related keywords for filtering
        self.industry_keywords = [
            # Core ESG terms
            'esg', 'environmental social governance', 'sustainability', 'sustainable development',
            'climate change', 'climate action', 'carbon', 'carbon footprint', 'emissions',
            'net zero', 'carbon neutral', 'carbon negative', 'decarbonization',
            'greenhouse gas', 'ghg', 'scope 1', 'scope 2', 'scope 3',
            
            # Sustainability frameworks
            'sbti', 'science based targets', 'cdp', 'tcfd', 'sasb', 'gri', 'ungc',
            'carbon disclosure project', 'task force on climate-related financial disclosures',
            'sustainability accounting standards board', 'global reporting initiative',
            
            # Carbon markets
            'carbon credits', 'carbon offset', 'carbon trading', 'carbon market',
            'voluntary carbon market', 'compliance carbon market',
            
            # Renewable energy
            'renewable energy', 'clean energy', 'green energy', 'solar power', 'solar energy',
            'wind power', 'wind energy', 'offshore wind', 'onshore wind', 'hydroelectric',
            'geothermal', 'biomass', 'bioenergy', 'hydrogen', 'green hydrogen',
            
            # Energy efficiency and management
            'energy efficiency', 'energy management', 'energy conservation',
            'smart grid', 'grid modernization', 'energy storage', 'battery storage',
            
            # Data centers and technology
            'data center', 'data centre', 'server farm', 'cloud computing',
            'green data center', 'sustainable technology', 'clean tech', 'cleantech',
            
            # RTO and grid operators
            'nyiso', 'caiso', 'pjm', 'ercot', 'ferc', 'rto', 'iso',
            'grid operator', 'transmission', 'electricity market', 'power market',
            'energy market', 'grid reliability', 'interconnection', 'miso',
            'midcontinent independent system operator',
            
            # Supply chain and manufacturing
            'supply chain', 'manufacturing', 'factory', 'industrial', 'value chain',
            'logistics', 'procurement', 'circular economy', 'biodiversity',
            
            # Policy and regulation
            'epa', 'environmental protection agency', 'energy policy', 'climate policy',
            'renewable energy policy', 'energy transition', 'clean energy transition'
        ]
        
        # Keywords that indicate irrelevant content (to exclude)
        self.exclude_keywords = [
            'sports', 'entertainment', 'celebrity', 'gossip', 'movie', 'music',
            'gaming', 'video game', 'casino', 'poker', 'betting', 'gambling',
            'crypto', 'bitcoin', 'ethereum', 'blockchain', 'nft', 'cryptocurrency',
            'stock market', 'trading', 'investment', 'finance', 'banking',
            'real estate', 'property', 'housing', 'mortgage', 'insurance',
            'health', 'medical', 'pharmaceutical', 'drug', 'medicine',
            'food', 'restaurant', 'cooking', 'recipe', 'diet', 'nutrition',
            'fashion', 'clothing', 'shopping', 'retail', 'consumer goods',
            'automotive', 'car', 'vehicle', 'transportation', 'travel', 'tourism',
            'politics', 'election', 'government', 'political party', 'campaign',
            'crime', 'police', 'law enforcement', 'legal', 'court', 'lawyer'
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
        """Check if an article is relevant to ESG/sustainability topics"""
        text = (title + ' ' + description).lower()
        
        # Only exclude completely off-topic content
        off_topic_keywords = [
            'sports', 'football', 'basketball', 'baseball', 'soccer', 'tennis', 'golf',
            'entertainment', 'celebrity', 'gossip', 'movie', 'music', 'hollywood',
            'gaming', 'video game', 'casino', 'poker', 'betting', 'gambling',
            'crypto', 'bitcoin', 'ethereum', 'blockchain', 'nft', 'cryptocurrency',
            'real estate', 'property', 'housing', 'mortgage', 'home buying',
            'health', 'medical', 'pharmaceutical', 'drug', 'medicine', 'disease',
            'food', 'restaurant', 'cooking', 'recipe', 'diet', 'nutrition',
            'fashion', 'clothing', 'shopping', 'retail', 'consumer goods',
            'automotive', 'car', 'vehicle', 'transportation', 'travel', 'tourism',
            'politics', 'election', 'government', 'political party', 'campaign',
            'crime', 'police', 'law enforcement', 'legal', 'court', 'lawyer'
        ]
        
        # Check for completely off-topic keywords
        for off_topic in off_topic_keywords:
            if off_topic in text:
                return False
        
        # If it's not completely off-topic, include it
        # This is much more lenient - we'll include most content and let the user decide
        return True

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
            
        # For Google Alerts, take more entries but still apply filtering
        max_entries = 100 if "Google Alert" in source_name else 20
            
        for entry in feed.entries[:max_entries]:
            title = entry.get('title', '')
            description = entry.get('description', '') or entry.get('summary', '')
            
            # Clean HTML tags from description
            description = re.sub(r'<[^>]+>', '', description)
            
            # Always check if article is relevant (including Google Alerts)
            if self.is_relevant(title, description):
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

    def is_duplicate(self, article1, article2):
        """Check if two articles are duplicates based on title similarity and URL"""
        # Check if URLs are the same (exact match)
        if article1['link'] == article2['link']:
            return True
        
        # Check if titles are very similar (fuzzy matching)
        title1 = article1['title'].lower().strip()
        title2 = article2['title'].lower().strip()
        
        # Remove common punctuation and extra spaces
        title1 = re.sub(r'[^\w\s]', '', title1)
        title2 = re.sub(r'[^\w\s]', '', title2)
        
        # If titles are identical after cleaning, they're duplicates
        if title1 == title2:
            return True
        
        # Check for high similarity (if one title contains the other)
        if len(title1) > 15 and len(title2) > 15:
            # If one title is contained within the other (with some tolerance)
            if title1 in title2 or title2 in title1:
                return True
            
            # Check for very similar titles (90% similarity threshold)
            words1 = set(title1.split())
            words2 = set(title2.split())
            
            if len(words1) > 3 and len(words2) > 3:
                intersection = words1.intersection(words2)
                union = words1.union(words2)
                similarity = len(intersection) / len(union)
                
                if similarity > 0.9:  # 90% similarity threshold (increased from 0.8)
                    return True
        
        return False

    def remove_duplicates(self, articles):
        """Remove duplicate articles from the list"""
        unique_articles = []
        seen_urls = set()
        
        for article in articles:
            # Check if we've seen this URL
            if article['link'] in seen_urls:
                continue
            
            # Check if this article is a duplicate of any existing article
            is_duplicate = False
            for existing_article in unique_articles:
                if self.is_duplicate(article, existing_article):
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_articles.append(article)
                seen_urls.add(article['link'])
        
        removed_count = len(articles) - len(unique_articles)
        if removed_count > 0:
            logger.info(f"Removed {removed_count} duplicate articles")
        
        return unique_articles

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
        
        # Remove duplicates before sorting
        logger.info(f"Total articles before deduplication: {len(self.all_articles)}")
        self.all_articles = self.remove_duplicates(self.all_articles)
        logger.info(f"Total articles after deduplication: {len(self.all_articles)}")
        
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
    
    # Export to CSV in Downloads folder
    csv_file = aggregator.export_to_csv(aggregator.all_articles)
    
    print(f"\n📊 Summary:")
    print(f"   - RSS Feed: feed.xml ({len(aggregator.all_articles)} articles)")
    print(f"   - CSV Export: {csv_file}")
    print(f"   - Location: Google Drive ESG News folder")
    print(f"\n✅ CSV file saved to Google Drive for easy access!")
