import pandas as pd
import os
import math

from django.utils.text import slugify
from django.utils import timezone

from .models import Record

def process_csvs(directory):
    for filename in os.listdir(directory):
        if filename.endswith("csv"):
            file_path = os.path.join(directory, filename)
            df = pd.read_csv(file_path)
            df = df.drop(columns=['Unnamed: 0'])
            df = clean_df(df)
            records = create_record_objects(df)
            send_to_api(records)

def clean_df(df):
    df = df.drop_duplicates()
    df['Price'] = df['Price'].apply(lambda row: currency_exchange(row))
    df['Score'] = df.apply(lambda row: score(row['Wants'], row['Haves'], row['Price']), axis=1)

def create_record_objects(df):
    records = []
    for _, row in df.iterrows:
        record = Record(
            discogs_id = row['ID'],
            artist = row['Artist'],
            title = row['Title'],
            format = row['Format'],
            seller = row['Seller'],
            subtitle = slugify(row['Title']),
            label = row['Label'], 
            catno = row['Catalog Number'], 
            media_condition = row['Condition'],
            record_price = row['Price'],
            wants = row['Wants'],
            haves = row['Haves'],
            score= row['Score'],
            added=timezone.now(),  # Or use the timestamp in the CSV if available
            processed=False  # Marking the record as unprocessed initially
            )
        records.append(record)
    Record.objects.bulk_create(records)

    return records

def send_to_api(processed_data):
    api_url = 'http:localhost:8000/api/'
    


def score(wants, haves, price):
    log_wants = math.log1p(wants)  
    log_ratio = math.log1p(wants / (haves + 1))   
    log_price = math.log1p(1 / price)
    score = log_wants * log_ratio * log_price
    return score

def currency_exchange(price):
    price = price.strip("()").replace("'", "")
    price, currency = price.split(", ")
    exchange_rate = get_exchange_rates().get(currency, 1)
    return (round(float(price) * exchange_rate, 2))

def get_exchange_rates():
        '''
        url = 'https://api.fxratesapi.com/latest'
        response = requests.get(url)
        data = response.json()
        rates = data.get('rates', {})
        
        return {
            'EUR': 1 / rates.get('EUR', 'N/A'),
            'JPY': 1 / rates.get('JPY', 'N/A'),
            'GBP': 1 / rates.get('GBP', 'N/A'),
            'BRL': 1 / rates.get('BRL', 'N/A'),
        }
        '''
        return {
            'EUR': 1 / 0.90,
            'JPY': 1 / 144.66,
            'GBP': 1 / 0.75,
            'BRL': 1 / 5.48,
            'CAD': 1 / 1.35,
        }
