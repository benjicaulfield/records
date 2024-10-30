from django.core.management.base import BaseCommand
from processing.models import Record

class Command(BaseCommand):
    help = 'Populate new fields in the Record model'

    def handle(self, *args, **kwargs):
        records = Record.objects.all()
        for record in records:
            if record.discogs_id:
                genres, styles, suggested_price = self.get_discogs_data(record.discogs_id)
                record.genres = genres
                record.styles = styles
                record.suggested_price = suggested_price
                record.save()
        self.stdout.write(self.style.SUCCESS('Successfully populated new fields'))

    def get_discogs_data(self, discogs_id):
        genres = []
        styles = []
        suggested_price = 0.00
        # Make a request to the Discogs API to get genres, styles, and suggested price
        return genres, styles, suggested_price