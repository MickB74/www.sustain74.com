#!/usr/bin/env python3
"""
ESG Newsletter Generator using Google Gemini
Generates professional ESG analyst newsletters from RSS feed content
"""

import xml.etree.ElementTree as ET
import requests
import json
import os
from datetime import datetime, timedelta
import logging
from typing import List, Dict, Any
import google.generativeai as genai

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ESGNewsletterGenerator:
    def __init__(self, gemini_api_key: str):
        """Initialize the newsletter generator with Gemini API key"""
        self.gemini_api_key = gemini_api_key
        genai.configure(api_key=gemini_api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
    def load_rss_feed(self, feed_path: str = 'feed.xml') -> List[Dict[str, Any]]:
        """Load and parse the RSS feed"""
        try:
            tree = ET.parse(feed_path)
            root = tree.getroot()
            
            articles = []
            for item in root.findall('.//item'):
                article = {
                    'title': item.find('title').text if item.find('title') is not None else '',
                    'description': item.find('description').text if item.find('description') is not None else '',
                    'link': item.find('link').text if item.find('link') is not None else '',
                    'pubDate': item.find('pubDate').text if item.find('pubDate') is not None else '',
                    'source': item.find('source').text if item.find('source') is not None else 'Unknown Source',
                    'categories': []
                }
                
                # Extract categories if available
                categories_elem = item.find('categories')
                if categories_elem is not None and categories_elem.text:
                    article['categories'] = [cat.strip() for cat in categories_elem.text.split(',')]
                
                articles.append(article)
            
            logger.info(f"Loaded {len(articles)} articles from RSS feed")
            return articles
            
        except Exception as e:
            logger.error(f"Error loading RSS feed: {e}")
            return []
    
    def filter_recent_articles(self, articles: List[Dict], days: int = 7) -> List[Dict]:
        """Filter articles from the last N days"""
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_articles = []
        
        for article in articles:
            try:
                # Parse various date formats
                pub_date_str = article['pubDate']
                if 'GMT' in pub_date_str or 'UTC' in pub_date_str:
                    pub_date = datetime.strptime(pub_date_str, '%a, %d %b %Y %H:%M:%S %Z')
                else:
                    pub_date = datetime.strptime(pub_date_str, '%a, %d %b %Y %H:%M:%S')
                
                if pub_date >= cutoff_date:
                    recent_articles.append(article)
            except Exception as e:
                logger.warning(f"Could not parse date for article: {article['title']} - {e}")
                # Include articles with unparseable dates
                recent_articles.append(article)
        
        logger.info(f"Filtered to {len(recent_articles)} recent articles")
        return recent_articles
    
    def prepare_articles_for_gemini(self, articles: List[Dict]) -> str:
        """Prepare articles in a format suitable for Gemini analysis"""
        articles_text = []
        
        for i, article in enumerate(articles[:20], 1):  # Limit to top 20 articles
            categories_str = ', '.join(article['categories']) if article['categories'] else 'General'
            articles_text.append(f"""
Article {i}:
Title: {article['title']}
Source: {article['source']}
Categories: {categories_str}
Description: {article['description']}
Link: {article['link']}
Published: {article['pubDate']}
---""")
        
        return '\n'.join(articles_text)
    
    def generate_newsletter_with_gemini(self, articles_text: str) -> str:
        """Use Gemini to generate the newsletter content"""
        
        prompt = f"""
You are a senior ESG analyst at Sustain74, a sustainability consulting firm. Your task is to create a professional weekly ESG newsletter for subscribers.

Based on the following recent ESG and sustainability news articles, create a comprehensive newsletter that includes:

1. **Executive Summary** (2-3 sentences): Key themes and trends from the week
2. **Top Stories** (5-7 stories): Most important developments with brief analysis
3. **Sector Highlights**: 
   - Carbon Credits & Markets
   - Renewable Energy
   - Data Centers & Technology
   - Regulatory & Policy Updates
4. **Market Implications**: What these developments mean for businesses and investors
5. **Looking Ahead**: Key events or trends to watch

**Writing Style:**
- Professional but accessible
- Include specific company names and data points
- Provide brief ESG analyst insights
- Use active voice and clear, concise language
- Include all relevant links from the articles

**Format:**
- Use markdown formatting
- Include article links in the text
- Group related stories together
- Add brief analyst commentary for each major story

Here are the recent articles to analyze:

{articles_text}

Generate a professional ESG analyst newsletter that would be valuable for sustainability professionals, investors, and business leaders.
"""

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Error generating newsletter with Gemini: {e}")
            return f"Error generating newsletter: {e}"
    
    def create_html_newsletter(self, markdown_content: str) -> str:
        """Convert markdown newsletter to HTML for email"""
        
        html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sustain74 ESG Weekly Newsletter</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f9f9f9;
        }}
        .container {{
            background-color: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .header {{
            text-align: center;
            border-bottom: 3px solid #2d5f8a;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        .header h1 {{
            color: #2d5f8a;
            margin: 0;
            font-size: 2.5em;
        }}
        .header p {{
            color: #666;
            margin: 10px 0 0 0;
            font-size: 1.1em;
        }}
        .date {{
            text-align: center;
            color: #888;
            font-style: italic;
            margin-bottom: 30px;
        }}
        h2 {{
            color: #2d5f8a;
            border-bottom: 2px solid #e0e0e0;
            padding-bottom: 10px;
            margin-top: 30px;
        }}
        h3 {{
            color: #444;
            margin-top: 25px;
        }}
        p {{
            margin-bottom: 15px;
        }}
        a {{
            color: #2d5f8a;
            text-decoration: none;
        }}
        a:hover {{
            text-decoration: underline;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #e0e0e0;
            text-align: center;
            color: #666;
            font-size: 0.9em;
        }}
        .highlight {{
            background-color: #f0f8ff;
            padding: 15px;
            border-left: 4px solid #2d5f8a;
            margin: 20px 0;
        }}
        ul {{
            padding-left: 20px;
        }}
        li {{
            margin-bottom: 8px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Sustain74 ESG Weekly Newsletter</h1>
            <p>Your trusted source for ESG insights and sustainability analysis</p>
        </div>
        
        <div class="date">
            {datetime.now().strftime('%B %d, %Y')}
        </div>
        
        <div class="content">
            {self.convert_markdown_to_html(markdown_content)}
        </div>
        
        <div class="footer">
            <p><strong>Sustain74</strong> | Professional ESG Consulting & Analysis</p>
            <p>Visit us at <a href="https://www.sustain74.com">www.sustain74.com</a></p>
            <p>For questions or to subscribe, contact: <a href="mailto:michael@sustain74.com">michael@sustain74.com</a></p>
        </div>
    </div>
</body>
</html>
"""
        return html_template
    
    def convert_markdown_to_html(self, markdown_text: str) -> str:
        """Simple markdown to HTML conversion for newsletter content"""
        import re
        
        # Convert **bold** to <strong>
        html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', markdown_text)
        
        # Convert *italic* to <em>
        html = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html)
        
        # Convert markdown links [text](url) to HTML
        html = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', html)
        
        # Convert headers
        html = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
        
        # Convert lists
        html = re.sub(r'^- (.*?)$', r'<li>\1</li>', html, flags=re.MULTILINE)
        html = re.sub(r'(\n<li>.*?</li>\n)+', r'<ul>\g<0></ul>', html, flags=re.DOTALL)
        
        # Convert paragraphs
        html = re.sub(r'\n\n([^<].*?)\n\n', r'<p>\1</p>', html, flags=re.DOTALL)
        
        return html
    
    def save_newsletter(self, content: str, filename: str = None) -> str:
        """Save the newsletter to a file"""
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'ESG_Newsletter_{timestamp}.html'
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"Newsletter saved as: {filename}")
            return filename
        except Exception as e:
            logger.error(f"Error saving newsletter: {e}")
            return None
    
    def generate_newsletter(self, days: int = 7) -> str:
        """Main method to generate the complete newsletter"""
        logger.info("Starting ESG newsletter generation...")
        
        # Load and filter articles
        articles = self.load_rss_feed()
        if not articles:
            return "Error: No articles found in RSS feed"
        
        recent_articles = self.filter_recent_articles(articles, days)
        if not recent_articles:
            return "Error: No recent articles found"
        
        # Prepare articles for Gemini
        articles_text = self.prepare_articles_for_gemini(recent_articles)
        
        # Generate newsletter content
        logger.info("Generating newsletter with Gemini...")
        markdown_content = self.generate_newsletter_with_gemini(articles_text)
        
        # Convert to HTML
        html_content = self.create_html_newsletter(markdown_content)
        
        # Save newsletter
        filename = self.save_newsletter(html_content)
        
        logger.info("Newsletter generation complete!")
        return filename

def main():
    """Main function to run the newsletter generator"""
    # Get Gemini API key from environment variable
    gemini_api_key = os.getenv('GEMINI_API_KEY')
    
    if not gemini_api_key:
        print("❌ Error: GEMINI_API_KEY environment variable not set")
        print("Please set your Gemini API key:")
        print("export GEMINI_API_KEY='your-api-key-here'")
        return
    
    # Initialize generator
    generator = ESGNewsletterGenerator(gemini_api_key)
    
    # Generate newsletter
    print("📧 Generating ESG Newsletter...")
    filename = generator.generate_newsletter(days=7)
    
    if filename:
        print(f"✅ Newsletter generated successfully!")
        print(f"📄 File: {filename}")
        print(f"🌐 Open in browser to preview")
        print(f"📧 Ready to send to subscribers")
    else:
        print("❌ Error generating newsletter")

if __name__ == "__main__":
    main()
