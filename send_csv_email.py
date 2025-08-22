#!/usr/bin/env python3
"""
Script to send ESG stories CSV file via email
"""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os
from datetime import datetime

def send_csv_email(csv_file='esg_stories.csv', recipient_email='michael@sustain74.com'):
    """Send CSV file via email"""
    
    # Email configuration - you'll need to update these with your email settings
    sender_email = "your-email@gmail.com"  # Update with your email
    sender_password = "your-app-password"   # Update with your app password
    
    # For Gmail, you'll need to use an App Password, not your regular password
    # Go to Google Account settings > Security > 2-Step Verification > App passwords
    
    subject = f"ESG Stories Report - {datetime.now().strftime('%Y-%m-%d')}"
    
    # Create message
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject
    
    # Email body
    body = f"""
    Hi Michael,
    
    Here's your daily ESG stories report.
    
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
    
    # Send email
    try:
        # For Gmail
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        
        text = msg.as_string()
        server.sendmail(sender_email, recipient_email, text)
        server.quit()
        
        print(f"✅ Email sent successfully to {recipient_email}")
        return True
        
    except Exception as e:
        print(f"❌ Error sending email: {e}")
        print("\nTo set up email sending:")
        print("1. Update sender_email and sender_password in this script")
        print("2. For Gmail, enable 2-factor authentication and create an App Password")
        print("3. Use the App Password instead of your regular password")
        return False

if __name__ == "__main__":
    print("📧 ESG Stories Email Sender")
    print("=" * 30)
    
    # Check if CSV file exists
    if os.path.exists('esg_stories.csv'):
        print(f"📊 Found CSV file: esg_stories.csv")
        send_csv_email()
    else:
        print("❌ CSV file not found. Run rss_aggregator.py first to generate the CSV.")
