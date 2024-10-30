from django.core.management.base import BaseCommand
from processing.models import Record
from django.db import transaction

class Command(BaseCommand):
    help = 'Remove duplicate records'

    def handle(self, *args, **kwargs):
        with transaction.atomic():
            records = Record.objects.all()
            unique_records = records.order_by('discogs_id', 'seller').distinct('discogs_id', 'seller')
            duplicates = records.exclude(id__in=unique_records.values_list('id', flat=True))

            for duplicate in duplicates:
                self.stdout.write(f'Deleting duplicate record: {duplicate}')
                duplicate.delete()

        self.stdout.write(self.style.SUCCESS('Duplicates removed successfully!'))