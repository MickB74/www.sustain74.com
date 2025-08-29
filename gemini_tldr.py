#!/usr/bin/env python3
"""
Gemini TLDR Generator for Sustain74 ESG News
Uses Google Gemini API to create a 2-paragraph summary of the latest ESG news
"""

import os
import feedparser
import google.generativeai as genai
from datetime import datetime
import json

class GeminiTLDRGenerator:
    def __init__(self):
        """Initialize the Gemini TLDR generator"""
        # Configure Gemini API
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
        # RSS feed URL
        self.feed_url = 'https://www.sustain74.com/feed.xml'
        
    def fetch_articles(self, max_articles=20):
        """Fetch articles from the RSS feed"""
        print("📡 Fetching articles from RSS feed...")
        
        try:
            feed = feedparser.parse(self.feed_url)
            articles = []
            
            for entry in feed.entries[:max_articles]:
                article = {
                    'title': entry.title,
                    'description': entry.get('summary', ''),
                    'link': entry.link,
                    'published': entry.get('published', ''),
                    'source': entry.get('source', 'Unknown')
                }
                articles.append(article)
            
            print(f"✅ Fetched {len(articles)} articles")
            return articles
            
        except Exception as e:
            print(f"❌ Error fetching articles: {e}")
            return []
    
    def prepare_articles_text(self, articles):
        """Prepare articles text for Gemini"""
        text = "Latest ESG and Energy News Articles:\n\n"
        
        for i, article in enumerate(articles, 1):
            text += f"{i}. {article['title']}\n"
            text += f"   Source: {article['source']}\n"
            text += f"   Summary: {article['description'][:200]}...\n"
            text += f"   Link: {article['link']}\n\n"
        
        return text
    
    def generate_tldr(self, articles):
        """Generate TLDR using Gemini API"""
        print("🤖 Generating TLDR with Gemini...")
        
        articles_text = self.prepare_articles_text(articles)
        
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
            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            print(f"❌ Error generating TLDR: {e}")
            return None
    
    def save_tldr(self, tldr_text, filename=None):
        """Save TLDR to file"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'tldr_summary_{timestamp}.txt'
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"ESG News TLDR Summary\n")
                f.write(f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}\n")
                f.write(f"{'='*50}\n\n")
                f.write(tldr_text)
                f.write(f"\n\n{'='*50}\n")
                f.write(f"Source: Sustain74 ESG News Feed\n")
                f.write(f"Feed URL: {self.feed_url}\n")
            
            print(f"✅ TLDR saved to: {filename}")
            return filename
            
        except Exception as e:
            print(f"❌ Error saving TLDR: {e}")
            return None
    
    def generate_and_save(self, max_articles=20):
        """Main method to generate and save TLDR"""
        print("🚀 Starting Gemini TLDR Generator...")
        print("=" * 50)
        
        # Fetch articles
        articles = self.fetch_articles(max_articles)
        if not articles:
            print("❌ No articles found")
            return None
        
        # Generate TLDR
        tldr_text = self.generate_tldr(articles)
        if not tldr_text:
            print("❌ Failed to generate TLDR")
            return None
        
        # Save TLDR
        filename = self.save_tldr(tldr_text)
        
        print("\n" + "=" * 50)
        print("📊 SUMMARY")
        print("=" * 50)
        print(f"✅ Articles processed: {len(articles)}")
        print(f"📄 TLDR saved: {filename}")
        print(f"\n📝 TLDR Preview:")
        print("-" * 30)
        print(tldr_text[:300] + "..." if len(tldr_text) > 300 else tldr_text)
        print("-" * 30)
        
        return filename

def main():
    """Main function"""
    try:
        generator = GeminiTLDRGenerator()
        generator.generate_and_save()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nMake sure to set your GEMINI_API_KEY environment variable:")
        print("export GEMINI_API_KEY='your_api_key_here'")

if __name__ == "__main__":
    main()
