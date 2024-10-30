import os
import shutil
import pandas as pd

from django.core.management.base import BaseCommand
from processing.models import Record, Seller, Listing
from ...utils import currency_exchange, score

class Command(BaseCommand):
    help = 'Process inventory CSV files'

    def handle(self, *args, **kwargs):
        folder_path = os.path.join(os.path.dirname(__file__), '../../inventories')
        self.process_inventory(folder_path)
        self.stdout.write(self.style.SUCCESS('Successfully processed inventory files'))
        
    def process_inventory(self, folder):
        archive_folder = os.path.join(folder, 'archive')
        os.makedirs(archive_folder, exist_ok=True)

        for filename in os.listdir(folder):
            if filename.endswith('.csv'):
                user = filename.split('_')[0]  # Extract username from filename, assuming format is 'username_date.csv'
                file_path = os.path.join(folder, filename)
                print(f"Processing file: {file_path}")
                df = pd.read_csv(file_path)
                df = df.drop_duplicates()
                currency = df['Price'].iloc[0].split(",")[1].strip(" '()")
                df['Price'] = df.apply(lambda row: currency_exchange(row['Price']), axis=1) 
                seller_name = df['Seller'].iloc[0]
                seller, _ = Seller.objects.get_or_create(name=seller_name, currency=currency)
                records = df.values.tolist()
                for record_data in records:
                    (discogs_id, media_condition, record_price, seller_name, format, artist, title, label, 
                     catno, wants, haves, genres, styles, suggestion) = record_data
                    
                    record, created = Record.objects.get_or_create(
                        discogs_id=discogs_id)
                    
                    if created:
                        record.artist = artist
                        record.title = title
                        record.format = format
                        record.label = label
                        record.catno = catno
                        record.wants = wants
                        record.haves = haves
                        record.genres = genres
                        record.styles = styles
                        record.suggested_price = suggestion

                        try:
                            record.save()
                        except Exception as e:
                            print(f"Error saving record: {e}")
                            continue
                    
                    record_score = score(wants, haves, record_price)

                    Listing.objects.create(seller=seller, record=record, price=record_price, media_condition=media_condition, score=record_score)


                print(f"Processed {seller.name}, {len(records)} records")    
                shutil.move(file_path, os.path.join(archive_folder, filename))