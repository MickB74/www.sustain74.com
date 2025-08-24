#!/usr/bin/env python3
"""
Test script for ESG Newsletter Generator
Demonstrates the functionality without requiring API key setup
"""

import os
import sys
from datetime import datetime

def test_without_api_key():
    """Test the newsletter generator structure without API key"""
    print("🧪 Testing ESG Newsletter Generator Structure")
    print("=" * 50)
    
    # Check if feed.xml exists
    if not os.path.exists('feed.xml'):
        print("❌ feed.xml not found. Please run RSS aggregator first:")
        print("   python rss_aggregator.py")
        return False
    
    print("✅ feed.xml found")
    
    # Check if we can import the generator
    try:
        from newsletter_generator import ESGNewsletterGenerator
        print("✅ Newsletter generator imported successfully")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    
    # Test RSS feed loading
    try:
        generator = ESGNewsletterGenerator("test-key")
        articles = generator.load_rss_feed()
        print(f"✅ Loaded {len(articles)} articles from RSS feed")
        
        if len(articles) > 0:
            print(f"📰 Sample article: {articles[0]['title'][:50]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing generator: {e}")
        return False

def show_setup_instructions():
    """Show setup instructions"""
    print("\n📋 Setup Instructions:")
    print("=" * 30)
    print("1. Get a Gemini API key from: https://makersuite.google.com/app/apikey")
    print("2. Set the environment variable:")
    print("   export GEMINI_API_KEY='your-api-key-here'")
    print("3. Run the newsletter generator:")
    print("   python newsletter_generator.py")
    print("\n📧 The generated HTML file will be ready to send to subscribers!")

def show_sample_output():
    """Show what the newsletter will look like"""
    print("\n📧 Sample Newsletter Structure:")
    print("=" * 35)
    print("""
    ┌─────────────────────────────────────┐
    │     Sustain74 ESG Newsletter        │
    │  Your trusted source for ESG insights│
    └─────────────────────────────────────┘
    
    📅 August 24, 2025
    
    📊 Executive Summary
    Key themes and trends from the week...
    
    🔥 Top Stories
    • [Article Title](link) - Brief analysis
    • [Article Title](link) - Brief analysis
    
    🏭 Sector Highlights
    • Carbon Credits & Markets
    • Renewable Energy
    • Data Centers & Technology
    • Regulatory & Policy Updates
    
    💼 Market Implications
    What these developments mean for businesses...
    
    🔮 Looking Ahead
    Key events and trends to watch...
    
    ┌─────────────────────────────────────┐
    │ Sustain74 | Professional ESG        │
    │ Consulting & Analysis               │
    │ www.sustain74.com                   │
    └─────────────────────────────────────┘
    """)

def main():
    """Main test function"""
    print("🚀 ESG Newsletter Generator Test")
    print("=" * 40)
    
    # Test basic functionality
    if test_without_api_key():
        print("\n✅ Basic functionality test passed!")
        
        # Show sample output
        show_sample_output()
        
        # Show setup instructions
        show_setup_instructions()
        
        print("\n🎯 Next Steps:")
        print("1. Get your Gemini API key")
        print("2. Set the environment variable")
        print("3. Run: python newsletter_generator.py")
        print("4. Open the generated HTML file")
        print("5. Copy content to your email service")
        
    else:
        print("\n❌ Test failed. Please check the errors above.")

if __name__ == "__main__":
    main()
