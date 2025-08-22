#!/usr/bin/env python3
"""
RSS Feed Aggregator for Sustain74
Fetches relevant ESG/sustainability stories from external sources
"""

import feedparser
import requests
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
import re
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RSSAggregator:
    def __init__(self):
        # External RSS feeds focused on ESG/sustainability
        self.external_feeds = [
            {
                'url': 'https://feeds.feedburner.com/GreentechMedia',
                'name': 'Greentech Media',
                'keywords': ['sustainability', 'renewable', 'clean energy', 'esg']
            },
            {
                'url': 'https://www.reuters.com/arcio/rss/tag/environment/',
                'name': 'Reuters Environment',
                'keywords': ['environment', 'climate', 'sustainability']
            },
            {
                'url': 'https://www.bloomberg.com/feeds/bgreen',
                'name': 'Bloomberg Green',
                'keywords': ['climate', 'green', 'sustainability', 'esg']
            },
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
                'url': 'https://www.ft.com/rss/home',
                'name': 'Financial Times',
                'keywords': ['esg', 'sustainability', 'climate', 'environment', 'carbon']
            },
            {
                'url': 'https://www.wsj.com/xml/rss/3_7085.xml',
                'name': 'Wall Street Journal',
                'keywords': ['esg', 'sustainability', 'climate', 'environment']
            },
            {
                'url': 'https://www.greenbiz.com/feed',
                'name': 'GreenBiz',
                'keywords': ['sustainability', 'esg', 'green business', 'climate']
            },
            {
                'url': 'https://www.corporateknights.com/feed/',
                'name': 'Corporate Knights',
                'keywords': ['sustainability', 'esg', 'corporate responsibility']
            },
            {
                'url': 'https://www.triplepundit.com/feed/',
                'name': 'TriplePundit',
                'keywords': ['sustainability', 'esg', 'social responsibility']
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
                'url': 'https://www.smartenergydecisions.com/feed/',
                'name': 'Smart Energy Decisions',
                'keywords': ['energy', 'smart energy', 'energy efficiency', 'renewable energy', 'sustainability', 'energy management']
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
            'renewable energy', 'solar', 'wind power', 'clean energy'
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

    def extract_articles(self, feed, source_name, keywords):
        """Extract relevant articles from a feed"""
        articles = []
        
        if not feed or not feed.entries:
            return articles
            
        # For Google Alerts, take more entries and skip filtering
        max_entries = 30 if "Google Alert" in source_name else 10
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
                
                # Only include articles from last 30 days
                if datetime.now() - pub_date <= timedelta(days=30):
                    articles.append({
                        'title': title,
                        'description': description[:300] + '...' if len(description) > 300 else description,
                        'link': entry.get('link', ''),
                        'pubDate': pub_date.strftime('%a, %d %b %Y %H:%M:%S GMT'),
                        'source': source_name,
                        'guid': entry.get('id', entry.get('link', ''))
                    })
        
        return articles

    def generate_rss(self, articles, max_items=20):
        """Generate RSS XML from articles"""
        # Create RSS root element
        rss = ET.Element('rss', version='2.0')
        rss.set('xmlns:atom', 'http://www.w3.org/2005/Atom')
        
        # Create channel
        channel = ET.SubElement(rss, 'channel')
        
        # Channel metadata
        ET.SubElement(channel, 'title').text = 'Sustain74 - ESG & Sustainability News'
        ET.SubElement(channel, 'description').text = 'Curated ESG and sustainability news from trusted sources'
        ET.SubElement(channel, 'link').text = 'https://www.sustain74.com'
        ET.SubElement(channel, 'language').text = 'en-us'
        ET.SubElement(channel, 'lastBuildDate').text = datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT')
        ET.SubElement(channel, 'generator').text = 'Sustain74 RSS Aggregator'
        
        # Self-referencing link
        atom_link = ET.SubElement(channel, 'atom:link')
        atom_link.set('href', 'https://www.sustain74.com/feed.xml')
        atom_link.set('rel', 'self')
        atom_link.set('type', 'application/rss+xml')
        
        # Add articles as items
        for article in articles[:max_items]:
            item = ET.SubElement(channel, 'item')
            
            ET.SubElement(item, 'title').text = article['title']
            ET.SubElement(item, 'description').text = article['description']
            ET.SubElement(item, 'link').text = article['link']
            ET.SubElement(item, 'pubDate').text = article['pubDate']
            ET.SubElement(item, 'source').text = article['source']
            ET.SubElement(item, 'guid').text = article['guid']
        
        return ET.tostring(rss, encoding='unicode', method='xml')

    def create_feed(self, output_file='feed.xml'):
        """Create the aggregated RSS feed"""
        all_articles = []
        
        # Skip external feeds - only use Google Alerts
        # for feed_config in self.external_feeds:
        #     feed = self.fetch_feed(feed_config['url'])
        #     if feed:
        #         articles = self.extract_articles(
        #             feed, 
        #             feed_config['name'], 
        #             feed_config['keywords']
        #         )
        #         all_articles.extend(articles)
        #         logger.info(f"Found {len(articles)} relevant articles from {feed_config['name']}")
        
        # Fetch articles from Google Alerts feeds only
        for feed_config in self.google_alerts_feeds:
            feed = self.fetch_feed(feed_config['url'])
            if feed:
                # Get all articles from Google Alerts without keyword filtering
                articles = self.extract_articles(
                    feed, 
                    feed_config['name'], 
                    []  # Empty keywords list to get all articles
                )
                all_articles.extend(articles)
                logger.info(f"Found {len(articles)} articles from {feed_config['name']}")
        
        # Sort articles by publication date (newest first)
        all_articles.sort(key=lambda x: x['pubDate'], reverse=True)
        
        # Generate RSS XML with higher max_items
        rss_xml = self.generate_rss(all_articles, max_items=50)
        
        # Add XML declaration
        xml_content = '<?xml version="1.0" encoding="UTF-8"?>\n' + rss_xml
        
        # Write to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(xml_content)
        
        logger.info(f"Created RSS feed with {len(all_articles)} articles: {output_file}")
        return len(all_articles)

def main():
    """Main function for testing"""
    aggregator = RSSAggregator()
    
    print("Sustain74 RSS Feed Aggregator")
    print("=" * 35)
    print("Fetching ESG and sustainability news from external sources...")
    
    try:
        article_count = aggregator.create_feed()
        print(f"\n✅ Successfully created RSS feed with {article_count} articles")
        print("📄 Feed saved as: feed.xml")
        print("🌐 Add this to your website at: https://www.sustain74.com/feed.xml")
        
    except Exception as e:
        print(f"\n❌ Error creating RSS feed: {e}")
        logger.error(f"Feed creation failed: {e}")

if __name__ == "__main__":
    main()
