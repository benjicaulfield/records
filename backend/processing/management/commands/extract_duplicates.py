import json

from django.core.management.base import BaseCommand
from django.db.models import Count
from processing.models import Record

class Command(BaseCommand):
    help = 'Extract duplicates from the Record model'

    def handle(self, *args, **kwargs):
        temp_listings = []
        duplicates = Record.objects.values('discogs_id').annotate(count=Count('discogs_id')).filter(count__gt=1)
        for duplicate in duplicates:
            discogs_id = duplicate['discogs_id']
            records = Record.objects.filter(discogs_id=discogs_id)
            keeper = records.first()
            
            for record in records:
                if record != keeper:
                    listing_data = {
                        'seller': record.seller,
                        'record': record.discogs_id,
                        'price': str(record.record_price),
                        'media_condition': record.media_condition,
                    }
                    temp_listings.append(listing_data)
                    record.delete()

        with open('duplicates.json', 'w') as f:
            json.dump(temp_listings, f, indent=4)
                
        self.stdout.write(self.style.SUCCESS('Successfully extracted duplicates'))