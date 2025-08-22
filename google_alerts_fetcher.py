#!/usr/bin/env python3
"""
Google Alerts RSS Fetcher for Sustain74
Fetches and processes Google Alerts RSS feeds for ESG and sustainability news
"""

import requests
import feedparser
import json
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging
from urllib.parse import urlparse
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GoogleAlertsFetcher:
    def __init__(self, cache_file: str = "news_cache.json"):
        self.cache_file = cache_file
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # ESG and sustainability keywords for Google Alerts
        self.recommended_keywords = [
            "ESG reporting",
            "sustainability regulations", 
            "climate disclosure",
            "renewable energy investment",
            "carbon neutrality",
            "sustainable finance",
            "green bonds",
            "net zero commitments",
            "SBTi scope 3",
            "CDP reporting",
            "ESG regulations",
            "sustainability standards",
            "clean energy transition",
            "circular economy",
            "climate risk disclosure"
        ]
        
        # Sample RSS feed URLs (replace with your actual Google Alerts RSS URLs)
        self.rss_feeds = [
            # Add your Google Alerts RSS feed URLs here
            # Example: "https://www.google.com/alerts/feeds/your-feed-id"
        ]

    def fetch_rss_feed(self, feed_url: str) -> Optional[List[Dict]]:
        """Fetch and parse an RSS feed"""
        try:
            logger.info(f"Fetching RSS feed: {feed_url}")
            response = self.session.get(feed_url, timeout=10)
            response.raise_for_status()
            
            # Parse the RSS feed
            feed = feedparser.parse(response.content)
            
            articles = []
            for entry in feed.entries:
                article = self.parse_rss_entry(entry)
                if article:
                    articles.append(article)
            
            logger.info(f"Fetched {len(articles)} articles from {feed_url}")
            return articles
            
        except Exception as e:
            logger.error(f"Error fetching RSS feed {feed_url}: {e}")
            return None

    def parse_rss_entry(self, entry) -> Optional[Dict]:
        """Parse a single RSS entry into our article format"""
        try:
            # Extract title and link
            title = entry.get('title', '').strip()
            url = entry.get('link', '')
            
            if not title or not url:
                return None
            
            # Extract description/summary
            description = entry.get('summary', '')
            if not description:
                description = entry.get('description', '')
            
            # Clean up HTML tags from description
            description = re.sub(r'<[^>]+>', '', description)
            description = description.strip()
            
            # Extract date
            published = entry.get('published_parsed') or entry.get('updated_parsed')
            if published:
                date = datetime(*published[:6])
            else:
                date = datetime.now()
            
            # Extract source from URL or feed
            source = self.extract_source(url)
            
            # Determine tags and category
            tags, category = self.categorize_article(title, description)
            
            return {
                'title': title,
                'excerpt': description[:300] + '...' if len(description) > 300 else description,
                'source': source,
                'date': date.strftime('%Y-%m-%d'),
                'url': url,
                'tags': tags,
                'category': category
            }
            
        except Exception as e:
            logger.error(f"Error parsing RSS entry: {e}")
            return None

    def extract_source(self, url: str) -> str:
        """Extract source name from URL"""
        try:
            domain = urlparse(url).netloc
            # Remove www. prefix
            if domain.startswith('www.'):
                domain = domain[4:]
            
            # Extract main domain
            source = domain.split('.')[0]
            
            # Capitalize and clean up
            source = source.replace('-', ' ').replace('_', ' ').title()
            
            return source
        except:
            return "Unknown Source"

    def categorize_article(self, title: str, description: str) -> tuple:
        """Categorize article based on content"""
        text = (title + ' ' + description).lower()
        
        tags = []
        category = 'sustainability'  # default
        
        # Define keyword mappings
        keyword_mappings = {
            'esg': ['esg', 'environmental social governance', 'sustainability reporting'],
            'climate': ['climate', 'carbon', 'emissions', 'global warming', 'greenhouse gas'],
            'renewable': ['renewable', 'solar', 'wind', 'clean energy', 'green energy'],
            'regulations': ['regulation', 'compliance', 'sec', 'eu', 'policy', 'law'],
            'sustainability': ['sustainability', 'sustainable', 'green', 'environmental']
        }
        
        # Check for matches
        for category_name, keywords in keyword_mappings.items():
            for keyword in keywords:
                if keyword in text:
                    if category_name not in tags:
                        tags.append(category_name)
                    if category == 'sustainability':  # Only update if still default
                        category = category_name
        
        # Ensure we have at least one tag
        if not tags:
            tags = ['sustainability']
        
        return tags, category

    def fetch_all_feeds(self) -> List[Dict]:
        """Fetch all configured RSS feeds"""
        all_articles = []
        
        for feed_url in self.rss_feeds:
            articles = self.fetch_rss_feed(feed_url)
            if articles:
                all_articles.extend(articles)
        
        # Sort by date (newest first)
        all_articles.sort(key=lambda x: x['date'], reverse=True)
        
        # Remove duplicates based on URL
        seen_urls = set()
        unique_articles = []
        for article in all_articles:
            if article['url'] not in seen_urls:
                seen_urls.add(article['url'])
                unique_articles.append(article)
        
        return unique_articles

    def get_sample_data(self) -> List[Dict]:
        """Return sample data for testing when no RSS feeds are configured"""
        return [
            {
                'title': "SEC Finalizes Climate Disclosure Rules for Public Companies",
                'excerpt': "The Securities and Exchange Commission has approved new rules requiring public companies to disclose climate-related risks and greenhouse gas emissions in their filings.",
                'source': "Reuters",
                'date': "2025-01-15",
                'url': "https://www.reuters.com/business/sustainable-business/sec-finalizes-climate-disclosure-rules-public-companies-2025-01-15/",
                'tags': ["regulations", "esg", "climate"],
                'category': "regulations"
            },
            {
                'title': "Major Tech Companies Commit to 100% Renewable Energy by 2030",
                'excerpt': "Leading technology companies including Google, Microsoft, and Apple have announced ambitious commitments to achieve 100% renewable energy usage across their global operations.",
                'source': "Bloomberg",
                'date': "2025-01-14",
                'url': "https://www.bloomberg.com/news/articles/2025-01-14/tech-giants-commit-to-100-renewable-energy-by-2030",
                'tags': ["renewable", "sustainability", "esg"],
                'category': "renewable"
            },
            {
                'title': "New Study Shows ESG-Focused Companies Outperform Market",
                'excerpt': "Research from Harvard Business School reveals that companies with strong ESG practices have consistently outperformed their peers in both financial returns and risk management.",
                'source': "Harvard Business Review",
                'date': "2025-01-13",
                'url': "https://hbr.org/2025/01/esg-focused-companies-outperform-market",
                'tags': ["esg", "sustainability"],
                'category': "esg"
            },
            {
                'title': "EU Introduces Stricter Carbon Border Adjustment Mechanism",
                'excerpt': "The European Union has implemented enhanced carbon border adjustment measures to ensure imported goods meet the same environmental standards as domestic production.",
                'source': "Financial Times",
                'date': "2025-01-12",
                'url': "https://www.ft.com/content/eu-carbon-border-adjustment-2025",
                'tags': ["regulations", "climate", "esg"],
                'category': "regulations"
            },
            {
                'title': "Renewable Energy Investment Reaches Record High in 2024",
                'excerpt': "Global investment in renewable energy projects reached $1.2 trillion in 2024, marking a 15% increase from the previous year and signaling strong market confidence.",
                'source': "IEA",
                'date': "2025-01-11",
                'url': "https://www.iea.org/reports/renewable-energy-investment-2024",
                'tags': ["renewable", "sustainability"],
                'category': "renewable"
            },
            {
                'title': "Corporate Net-Zero Commitments Accelerate Climate Action",
                'excerpt': "Analysis shows that corporate net-zero commitments have increased by 40% in the past year, with over 2,000 companies now committed to carbon neutrality.",
                'source': "Science Based Targets",
                'date': "2025-01-10",
                'url': "https://sciencebasedtargets.org/net-zero-commitments-2024",
                'tags': ["climate", "sustainability", "esg"],
                'category': "climate"
            }
        ]

    def save_to_cache(self, articles: List[Dict]):
        """Save articles to cache file"""
        try:
            cache_data = {
                'timestamp': datetime.now().isoformat(),
                'articles': articles
            }
            with open(self.cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
            logger.info(f"Saved {len(articles)} articles to cache")
        except Exception as e:
            logger.error(f"Error saving to cache: {e}")

    def load_from_cache(self) -> Optional[List[Dict]]:
        """Load articles from cache file"""
        try:
            with open(self.cache_file, 'r') as f:
                cache_data = json.load(f)
            
            # Check if cache is less than 1 hour old
            cache_time = datetime.fromisoformat(cache_data['timestamp'])
            if datetime.now() - cache_time < timedelta(hours=1):
                logger.info("Loading articles from cache")
                return cache_data['articles']
            else:
                logger.info("Cache is stale, will fetch fresh data")
                return None
        except FileNotFoundError:
            logger.info("No cache file found")
            return None
        except Exception as e:
            logger.error(f"Error loading from cache: {e}")
            return None

    def get_news_data(self) -> List[Dict]:
        """Main method to get news data"""
        # Try to load from cache first
        cached_articles = self.load_from_cache()
        if cached_articles:
            return cached_articles
        
        # If no RSS feeds configured, return sample data
        if not self.rss_feeds:
            logger.info("No RSS feeds configured, returning sample data")
            sample_data = self.get_sample_data()
            self.save_to_cache(sample_data)
            return sample_data
        
        # Fetch fresh data from RSS feeds
        articles = self.fetch_all_feeds()
        
        if articles:
            self.save_to_cache(articles)
            return articles
        else:
            # Fallback to sample data
            logger.warning("No articles fetched, falling back to sample data")
            sample_data = self.get_sample_data()
            self.save_to_cache(sample_data)
            return sample_data

def main():
    """Main function for testing"""
    fetcher = GoogleAlertsFetcher()
    
    print("Google Alerts Fetcher for Sustain74")
    print("=" * 40)
    
    if not fetcher.rss_feeds:
        print("\nNo RSS feeds configured.")
        print("To set up Google Alerts RSS feeds:")
        print("1. Go to https://www.google.com/alerts")
        print("2. Create alerts for ESG keywords")
        print("3. Choose 'RSS feed' as delivery method")
        print("4. Add the RSS feed URLs to the rss_feeds list in this script")
        print("\nRecommended keywords:")
        for keyword in fetcher.recommended_keywords:
            print(f"  - {keyword}")
    
    print("\nFetching news data...")
    articles = fetcher.get_news_data()
    
    print(f"\nFound {len(articles)} articles:")
    for i, article in enumerate(articles[:5], 1):  # Show first 5
        print(f"\n{i}. {article['title']}")
        print(f"   Source: {article['source']}")
        print(f"   Date: {article['date']}")
        print(f"   Tags: {', '.join(article['tags'])}")
        print(f"   Category: {article['category']}")

if __name__ == "__main__":
    main()
