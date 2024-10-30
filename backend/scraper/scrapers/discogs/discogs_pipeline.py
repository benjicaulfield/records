import os
import json
import requests
import pandas as pd
from dotenv import load_dotenv
from django.dispatch import Signal
from datetime import datetime
import discogs_client
from gmail import get_usernames, get_gmail_service
from user_inventory import authenticate_client, get_inventory

load_dotenv()

consumer_key = os.getenv('DISCOGS_CONSUMER_KEY')
consumer_secret = os.getenv('DISCOGS_CONSUMER_SECRET')
TOKEN_FILE = 'discogs_token.json'
INVENTORY_FILE = 'user_inventories.json'

INVENTORIES_FOLDER = 'inventories'

def pipeline():
    if not os.path.exists('inventories'):
        os.makedirs('inventories')
    service = get_gmail_service()
    userlist = get_usernames(service, 'dotdashdashdot - Shop New Wantlist Items for Sale')
    d = authenticate_client()
    today = datetime.now().strftime('%Y-%m-%d')
    for user in userlist:
        try:
            inventory = get_inventory(user)
            df = pd.DataFrame(inventory, columns=['ID', 'Condition', 'Price', 'Seller', 'Format', 'Artist', 'Title', 'Label', 'Catalog Number', 'Wants', 'Haves', 'Genres', 'Styles', 'Year', 'Suggested Price'])
            df = df.drop_duplicates(subset=['ID'])
            df[['Price', 'Suggested Price']] = df[['Price', 'Suggested Price']].astype(str)            
            df.to_csv(f'inventories/{user}_{today}.csv', index=False)
            records = df.to_dict(orient='records')
            data_list = []
            for record in records:
                data = {
                    "discogs_id": record.get("ID"),
                    "media_condition": record.get("Condition"),
                    "artist": record.get("Artist"),
                    "title": record.get("Title"),
                    "format": record.get("Format", ""),
                    "seller": record.get("Seller", ""),
                    "label": record.get("Label", ""),
                    "catno": record.get("Catalog Number"),
                    "record_price": record.get("Price", ""),
                    "wants": int(record.get("Wants", 0)),
                    "haves": int(record.get("Haves", 0)),
                    "genres": record.get("Genres", ""),
                    "styles": record.get("Styles", ""),
                    "year": record.get("Year", ""),
                    "suggested_price": record.get("Suggested Price", "")
                }
                data_list.append(data)

            json_data = json.dumps(data_list)
            response = requests.post(
                "http://localhost:8000/processing/data/receive/", 
                data=json_data, 
                headers={'Content-Type': 'application/json'}
            )

            if response.status_code == 201:
                print(f"Successfully processed record for {user}")
            elif response.status_code == 400:
                try:
                    error_data = response.json()
                    print(f"Serializer Errors: {error_data}")
                except json.JSONDecodeError:
                    print(f"Error (400): {response.text}")
            else:
                try:
                    error_data = response.json()
                    print(f"Server Error ({response.status_code}): {error_data}")
                except json.JSONDecodeError:
                    print(f"Error ({response.status_code}): {response.text}")
        except discogs_client.exceptions.HTTPError as e:
            print(f"Error fetching inventory for {user}: {e}")
            continue
    