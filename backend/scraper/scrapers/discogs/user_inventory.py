import os
import json
from dotenv import load_dotenv
import discogs_client
from discogs_client.exceptions import HTTPError
import time
import pandas as pd
from datetime import datetime
import random

from gmail import get_gmail_service, get_usernames

load_dotenv()

consumer_key = os.getenv('DISCOGS_CONSUMER_KEY')
consumer_secret = os.getenv('DISCOGS_CONSUMER_SECRET')
TOKEN_FILE = 'discogs_token.json'
INVENTORY_FILE = 'user_inventories.json'

INVENTORIES_FOLDER = 'inventories'


def load_inventory_json():
    if os.path.exists(INVENTORY_FILE):
        with open(INVENTORY_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_inventory_json(inventory):
    with open(INVENTORY_FILE, 'w') as f:
        json.dump(inventory, f, indent=4)

def update_user_inventory(username, record_ids):
    data = load_inventory_json()
    today = datetime.now().strftime('%Y-%m-%d')
    if username not in data:
        data[username] = {
            "last_inventory": today,
            "record_ids": record_ids
        }
    else:
        existing_ids = set(data[username]['record_ids'])
        new_ids = set(record_ids)
        all_ids = existing_ids.union(new_ids)
        data[username] = {
            "last_inventory": today,
            "record_ids": list(all_ids[-50:])
        }
    
    save_inventory_json(data)

def load_tokens():
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'r') as f:
            return json.load(f)
    return None

def save_tokens(token, secret):
    with open(TOKEN_FILE, 'w') as f:
        json.dump({'token': token, 'secret': secret}, f)

def authenticate_client():
    tokens = load_tokens()
    if tokens:
        d = discogs_client.Client('wantlist/1.0')
        d.set_consumer_key(consumer_key, consumer_secret)
        d.set_token(tokens['token'], tokens['secret'])
    else:
        # Perform OAuth flow if no tokens are found
        d = discogs_client.Client('wantlist/1.0')
        d.set_consumer_key(consumer_key, consumer_secret)
        token, secret, url = d.get_authorize_url()
        print(f"Please visit this URL to authorize: {url}")
        verifier = input("Enter the verifier code: ")
        access_token, access_secret = d.get_access_token(verifier)

        # Save the tokens for future use
        save_tokens(access_token, access_secret)

    return d

d = authenticate_client()

try:
    print(d.identity())
except discogs_client.exceptions.HTTPError as e:
        print(f"Error during authentication: {e}")

today = datetime.now().strftime('%Y-%m-%d')

service = get_gmail_service()
userlist = get_usernames(service, 'dotdashdashdot - Shop New Wantlist Items for Sale')
print(userlist)

def get_inventory(username):
    records = []
    user = d.user(username)
    inventory = user.inventory
    inventory.per_page = 250

    previous_inventory = load_inventory_json().get(username, {})
    previous_ids = set(previous_inventory.get('record_ids', []))

    current_ids = []

    for i in range(100):
        try:
            page = inventory.page(i)
            page_records = filter_page(page)
            for record in page_records:
                if record[0] in previous_ids:  # Check if the ID is in the previously collected IDs
                    update_user_inventory(username, current_ids)
                    return records
                current_ids.append(record[0])
            records += page_records
            time.sleep(random.randint(2, 3))

        except HTTPError as e:
            if e.status_code == 404:
                print(f"Page {i} for user {username}: User does not exist or may have been deleted. Skipping.")
                break  # Optionally, break if the user might not exist, or continue with `pass` if the user exists
            else:
                print(f"HTTPError occurred on page {i} for user {username}: {e}. Skipping page.")
                continue  # Continue to the next page if it's an HTTPError other than 404
        
        except Exception as e:
            print(f"Error fetching page {i} for user {username}: {e}. Skipping page.")
            continue  # Continue to the next page for other exceptions

    return records

def filter_page(page):
    conditions = {"Near Mint (NM or M-)", "Very Good Plus (VG+)", "Very Good (VG)", "Good Plus (G+)"}
    keepers = []
    for listing in page:
        if 'LP' in listing.data['release']['format'] and wanted(listing) and listing.condition in conditions:
            print(listing)
            keepers.append(parse_listing(listing))
    return keepers

def parse_listing(l):
    _id = l.release.id
    _condition = l.condition
    _price = (l.price.value, l.price.currency)
    _seller = l.seller.username
    _artist = l.release.data['artist']
    _format = l.release.data['format']
    _title = l.release.data['title']
    _label = l.release.data['label']
    _catno = l.release.data['catalog_number']
    _wants = l.release.data['stats']['community']['in_wantlist']
    _haves = l.release.data['stats']['community']['in_collection']
    _genres = l.release.genres
    _styles = l.release.styles
    _year = l.release.year
    _suggested_price = l.release.price_suggestions.very_good_plus 
    return (_id, _condition, _price, _seller, _format, _artist, _title, _label, _catno, _wants, _haves, _genres, _styles, _year, _suggested_price)

def wanted(listing):
    return listing.data['release']['stats']['community']['in_wantlist'] > listing.data['release']['stats']['community']['in_collection']

if "__main__" == __name__:
    for user in userlist:
        inventory = get_inventory(user)
        df = pd.DataFrame(inventory, columns=['ID', 'Condition', 'Price', 'Seller', 'Format', 'Artist', 'Title', 'Label', 'Catalog Number', 'Wants', 'Haves'])
        df.to_csv(f'inventories/{user}_{today}.csv', index=False)
    #   print(f'{user} inventory saved to {user}_{today}.csv')

