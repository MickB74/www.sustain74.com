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
            
            # Add categories as comma-separated string
            if article.get('categories'):
                ET.SubElement(item, 'categories').text = ','.join(article['categories'])
        
        return ET.tostring(rss, encoding='unicode', method='xml')

    def create_feed(self, output_file='feed.xml'):
        """Create the aggregated RSS feed"""
        all_articles = []
        
        # Fetch articles from external feeds
        for feed_config in self.external_feeds:
            feed = self.fetch_feed(feed_config['url'])
            if feed:
                articles = self.extract_articles(
                    feed, 
                    feed_config['name'], 
                    feed_config['keywords']
                )
                all_articles.extend(articles)
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
                all_articles.extend(articles)
                logger.info(f"Found {len(articles)} articles from {feed_config['name']}")
        
        # Sort articles by publication date (newest first)
        all_articles.sort(key=lambda x: x['pubDateObj'], reverse=True)
        
        # Generate RSS XML with higher max_items
        rss_xml = self.generate_rss(all_articles, max_items=100)
        
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
