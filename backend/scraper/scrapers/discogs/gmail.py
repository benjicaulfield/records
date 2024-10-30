from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.errors import HttpError

from bs4 import BeautifulSoup as bs
import datetime
import pickle
import base64
import os
import re

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
TOKEN_PATH = 'gmail_token.pickle'
CREDENTIALS_PATH = '/Users/benjamincaulfield/Documents/Documents/records/backend/scraper/scrapers/discogs/credentials.json'


def authenticate_gmail():
    creds = None
    if os.path.exists(TOKEN_PATH):
        print("Loading credentials from token.pickle...")
        with open(TOKEN_PATH, 'rb') as token:
            creds = pickle.load(token)
        print("Credentials loaded.")
    
    if not creds or not creds.valid:
        print("Credentials not valid or missing, re-authenticating...")
        if creds and creds.expired and creds.refresh_token:
            print("Refreshing expired credentials...")
            creds.refresh(Request())
        else:
            print("Initiating new authentication flow...")
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
            with open(TOKEN_PATH, 'wb') as token:
                pickle.dump(creds, token)
            print("New credentials saved.")

    return creds

    
def get_gmail_service():
    creds = authenticate_gmail()
    service = build('gmail', 'v1', credentials=creds)
    return service

def extract_usernames(text):
    usernames = re.findall(r'(?i)Seller:\s*([\w-]+)(?=\s*Rating|$)', text)
    return [username.replace('Seller', '').strip() for username in usernames]

def get_usernames(service, subject):
    usernames = []

    try:
        now = datetime.datetime.utcnow()
        past_30_hours = now - datetime.timedelta(hours=30)
        formatted_date = past_30_hours.strftime('%Y/%m/%d')
        search_query = f"subject:{subject} after:{formatted_date}"

        results = service.users().messages().list(userId='me', q=search_query).execute()
        messages = results.get('messages', [])

        if not messages:
            pass
        else:
            for message in messages:
                msg = service.users().messages().get(userId='me', id=message['id']).execute()
                parts = msg['payload'].get('parts', [])
                for part in parts:
                    mime_type = part.get('mimeType')
                    body = part.get('body', {})
                    data = body.get('data')

                    if mime_type == 'text/plain':
                        email_body = base64.urlsafe_b64decode(data.encode('UTF-8')).decode('UTF-8')
                        usernames = extract_usernames(email_body)
                        
                    elif mime_type == 'text/html':
                        email_body = base64.urlsafe_b64decode(data.encode('UTF-8')).decode('UTF-8')
                        soup = bs(email_body, 'html.parser')
                        text = soup.get_text()
                        usernames = extract_usernames(text)

    except HttpError as error:
        print(f'An error occurred: {error}')

    return usernames

service = get_gmail_service()
userlist = get_usernames(service, 'dotdashdashdot - Shop New Wantlist Items for Sale')
print(userlist)
