from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from .models import Record, Listing, Seller
from .serializers import RecordSerializer
import logging
import pandas as pd
from io import StringIO
import os

logger = logging.getLogger(__name__)

class ProcessDataView(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        records_to_create = []
        listings_to_create = []

        for record_data in data:
            # Handle the record part
            record, _ = Record.objects.get_or_create(
                discogs_id=record_data['discogs_id'],
                defaults={
                    'artist': record_data['artist'],
                    'title': record_data['title'],
                    'format': record_data['format'],
                    'label': record_data['label'],
                    'catno': record_data['catno'],
                    'wants': record_data['wants'],
                    'haves': record_data['haves'],
                    'genres': record_data['genres'],
                    'styles': record_data['styles'],
                    'suggested_price': self.clean_suggested_price(record_data['suggested_price']),
                    'year': record_data.get('year', None)  # Ensure 'year' is optional
                }
            )

            record_price = self.currency_exchange(record_data['record_price'])

            seller, _ = Seller.objects.get_or_create(
                name=record_data['seller'],
                currency=record_data['record_price'].split(", ")[1]
            )

            listing_data = {
                'seller': seller,
                'record': record,
                'record_price': record_price, 
                'media_condition': record_data['media_condition'],
                'kept': False,
                'evaluated': False
            }
            listings_to_create.append(Listing(**listing_data))

        if listings_to_create:
            Listing.objects.bulk_create(listings_to_create)

        return Response({"message": "Data processed successfully"}, status=status.HTTP_201_CREATED)

    
    def get_exchange_rates(self):
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
        }

    def currency_exchange(self, price):
        price = price.strip("()").replace("'", "")
        price, currency = price.split(", ")
        exchange_rate = self.get_exchange_rates().get(currency, 1)
        return round(float(price) * exchange_rate, 2)
    
    def clean_suggested_price(self, price):
        _, price, currency = price.split(" ")
        exchange_rate = self.get_exchange_rates().get(currency, 1)
        price = round(float(price) * exchange_rate, 2)
        return price
    
    def process_inventories(self, folder):
        for filename in os.listdir(folder):
            if filename.endswith('.csv'):
                user = filename.split('_')[0]  # Extract username from filename, assuming format is 'username_date.csv'
                file_path = os.path.join(folder, filename)
                print(f"Processing file: {file_path}")

                df = pd.read_csv(file_path)
                records = df.values.tolist()
                for record_data in records:
                    print(record_data)
                    (discogs_id, media_condition, record_price, seller_name, format, artist, title, label, 
                     catno, wants, haves, genres, styles, suggestion) = record_data
                    record, created = Record.objects.get_or_create(
                        discogs_id=discogs_id)
                seller, _ = Seller.objects.get_or_create(name=seller_name, currency=record_price.split(", ")[1])
                record_price = self.currency_exchange(record_price)
                Listing.objects.create(seller=seller, record=record, price=record_price, media_condition=media_condition)

                