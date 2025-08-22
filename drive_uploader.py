#!/usr/bin/env python3
"""
Script to upload ESG stories CSV file to Google Drive
"""

import os
import pickle
from datetime import datetime
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive.file']

def authenticate_google_drive():
    """Authenticate with Google Drive API"""
    creds = None
    
    # The file token.pickle stores the user's access and refresh tokens
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    # If there are no (valid) credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    return creds

def upload_to_drive(file_path, folder_name="ESG Stories"):
    """Upload file to Google Drive"""
    try:
        # Authenticate
        creds = authenticate_google_drive()
        service = build('drive', 'v3', credentials=creds)
        
        # Create folder if it doesn't exist
        folder_id = create_or_get_folder(service, folder_name)
        
        # Prepare file metadata
        file_metadata = {
            'name': f"ESG_Stories_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            'parents': [folder_id]
        }
        
        # Upload file
        media = MediaFileUpload(file_path, mimetype='text/csv', resumable=True)
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id,name,webViewLink'
        ).execute()
        
        print(f"✅ File uploaded successfully!")
        print(f"📁 File ID: {file.get('id')}")
        print(f"📄 File Name: {file.get('name')}")
        print(f"🔗 View Link: {file.get('webViewLink')}")
        
        return file.get('id')
        
    except HttpError as error:
        print(f"❌ An error occurred: {error}")
        return None

def create_or_get_folder(service, folder_name):
    """Create folder if it doesn't exist, or get existing folder ID"""
    try:
        # Search for existing folder
        results = service.files().list(
            q=f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false",
            spaces='drive',
            fields='files(id, name)'
        ).execute()
        
        folders = results.get('files', [])
        
        if folders:
            # Folder exists, return its ID
            folder_id = folders[0]['id']
            print(f"📁 Using existing folder: {folder_name}")
            return folder_id
        else:
            # Create new folder
            folder_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            
            folder = service.files().create(
                body=folder_metadata,
                fields='id'
            ).execute()
            
            folder_id = folder.get('id')
            print(f"📁 Created new folder: {folder_name}")
            return folder_id
            
    except HttpError as error:
        print(f"❌ Error with folder operation: {error}")
        return None

def setup_instructions():
    """Print setup instructions"""
    print("\n🔧 Google Drive Setup Instructions:")
    print("=" * 40)
    print("1. Go to Google Cloud Console: https://console.cloud.google.com/")
    print("2. Create a new project or select existing one")
    print("3. Enable the Google Drive API")
    print("4. Go to 'Credentials' and create 'OAuth 2.0 Client IDs'")
    print("5. Download the credentials JSON file")
    print("6. Rename it to 'credentials.json' and place it in this directory")
    print("7. Run this script - it will open a browser for authentication")
    print("\n📁 Files will be uploaded to a folder called 'ESG Stories' in your Google Drive")

def main():
    """Main function"""
    print("📤 Google Drive CSV Uploader")
    print("=" * 30)
    
    # Check if credentials file exists
    if not os.path.exists('credentials.json'):
        print("❌ credentials.json not found!")
        setup_instructions()
        return
    
    # Check if CSV file exists
    csv_file = 'esg_stories.csv'
    if not os.path.exists(csv_file):
        print(f"❌ {csv_file} not found!")
        print("Run rss_aggregator.py first to generate the CSV file.")
        return
    
    print(f"📊 Found CSV file: {csv_file}")
    print(f"📁 Will upload to Google Drive folder: 'ESG Stories'")
    
    # Upload to Google Drive
    file_id = upload_to_drive(csv_file)
    
    if file_id:
        print(f"\n✅ Success! Your CSV file is now in your Google Drive.")
        print(f"📊 You can view it at: https://drive.google.com/drive/folders/")
    else:
        print(f"\n❌ Upload failed. Check the error messages above.")

if __name__ == "__main__":
    main()
