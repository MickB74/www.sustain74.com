#!/usr/bin/env python3
"""
Script to send ESG stories CSV file via Gmail
"""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os
from datetime import datetime

def send_csv_email(csv_file='esg_stories.csv', recipient_email='michael@sustain74.com'):
    """Send CSV file via Gmail"""
    
    # Gmail configuration - UPDATE THESE WITH YOUR ACTUAL CREDENTIALS
    sender_email = "your-gmail@gmail.com"  # Replace with your Gmail address
    sender_password = "your-16-char-app-password"   # Replace with your App Password
    
    subject = f"ESG Stories Report - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    
    # Create message
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject
    
    # Email body
    body = f"""
    Hi Michael,
    
    Here's your ESG stories report with the latest articles from your RSS feed.
    
    📊 Report Details:
    - Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    - File: {os.path.basename(csv_file)}
    - Articles: {count_articles_in_csv(csv_file)} stories
    
    📋 The CSV file contains:
    - Date and time of publication
    - Article title and description
    - Source and direct link
    - Categories/tags assigned (carbon, renewable, datacenters, esg, technology, supplychain, rto)
    
    📁 Sources included:
    - Google Alerts (ESG & Energy, CAISO, ERCOT, Carbon Credits, OBBBA Renewables, SBTi, PJM)
    - External RSS feeds (Climate Change News, ESG Today, Corporate Knights, Data Center Knowledge)
    
    Best regards,
    Sustain74 RSS Aggregator
    """
    
    msg.attach(MIMEText(body, 'plain'))
    
    # Attach CSV file
    if os.path.exists(csv_file):
        with open(csv_file, "rb") as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
        
        encoders.encode_base64(part)
        part.add_header(
            'Content-Disposition',
            f'attachment; filename= {os.path.basename(csv_file)}'
        )
        msg.attach(part)
        
        print(f"📎 Attached file: {csv_file}")
    else:
        print(f"❌ CSV file not found: {csv_file}")
        return False
    
    # Send email via Gmail
    try:
        print(f"📧 Connecting to Gmail SMTP...")
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        
        print(f"🔐 Authenticating with Gmail...")
        server.login(sender_email, sender_password)
        
        print(f"📤 Sending email to {recipient_email}...")
        text = msg.as_string()
        server.sendmail(sender_email, recipient_email, text)
        server.quit()
        
        print(f"✅ Email sent successfully to {recipient_email}")
        return True
        
    except smtplib.SMTPAuthenticationError:
        print(f"❌ Authentication failed!")
        print("\n🔧 Gmail Setup Instructions:")
        print("1. Enable 2-Factor Authentication on your Gmail account")
        print("2. Go to Google Account settings: https://myaccount.google.com/")
        print("3. Security → 2-Step Verification → App passwords")
        print("4. Generate a new app password for 'Mail'")
        print("5. Update sender_email and sender_password in this script")
        print("6. Use the 16-character app password (not your regular password)")
        return False
        
    except Exception as e:
        print(f"❌ Error sending email: {e}")
        return False

def count_articles_in_csv(csv_file):
    """Count the number of articles in the CSV file"""
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            # Count lines minus header
            lines = f.readlines()
            return len(lines) - 1 if len(lines) > 1 else 0
    except:
        return "unknown"

def gmail_setup_instructions():
    """Print detailed Gmail setup instructions"""
    print("\n🔧 Gmail Setup Instructions:")
    print("=" * 50)
    print("1. Enable 2-Factor Authentication:")
    print("   - Go to https://myaccount.google.com/")
    print("   - Security → 2-Step Verification → Turn it on")
    print()
    print("2. Create App Password:")
    print("   - Go to https://myaccount.google.com/")
    print("   - Security → 2-Step Verification → App passwords")
    print("   - Select 'Mail' and 'Other (Custom name)'")
    print("   - Name it 'Sustain74 RSS'")
    print("   - Copy the 16-character password")
    print()
    print("3. Update the script:")
    print("   - Open send_csv_email.py")
    print("   - Replace 'your-gmail@gmail.com' with your actual Gmail")
    print("   - Replace 'your-16-char-app-password' with the app password")
    print()
    print("4. Test the email:")
    print("   - Run: python send_csv_email.py")

if __name__ == "__main__":
    print("📧 ESG Stories Email Sender (Gmail)")
    print("=" * 40)
    
    # Check if CSV file exists
    if os.path.exists('esg_stories.csv'):
        print(f"📊 Found CSV file: esg_stories.csv")
        
        # Check if credentials are configured
        with open('send_csv_email.py', 'r') as f:
            content = f.read()
            if 'your-gmail@gmail.com' in content or 'your-16-char-app-password' in content:
                print("⚠️  Gmail credentials not configured!")
                gmail_setup_instructions()
            else:
                send_csv_email()
    else:
        print("❌ CSV file not found. Run rss_aggregator.py first to generate the CSV.")
