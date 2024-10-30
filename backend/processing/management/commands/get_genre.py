import os
import discogs_client
from dotenv import load_dotenv

from django.core.management.base import BaseCommand
from scraper.scrapers.discogs.user_inventory import authenticate_client

load_dotenv()

consumer_key = os.getenv('DISCOGS_CONSUMER_KEY')
consumer_secret = os.getenv('DISCOGS_CONSUMER_SECRET')
TOKEN_FILE = 'discogs_token.json'

class Command(BaseCommand):
    help = 'Get genre from the Record model'
    d = authenticate_client()

    try:
        print(d.identity())
    except discogs_client.exceptions.HTTPError as e:
            print(f"Error during authentication: {e}")
    
    for filename in os.listdir('inventories'):
        if filename.endswith('.csv'):
            user = filename.split('_')[0]
            print(f"Processing file: {filename}")
            with open(f'inventories/{filename}', 'r') as f:
                print(f.read())