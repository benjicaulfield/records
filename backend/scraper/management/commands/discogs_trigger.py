from django.core.management.base import BaseCommand
from scraper.scrapers.discogs import discogs_pipeline

class Command(BaseCommand):
    help = "Trigger the Discogs scraper"

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Starting Discogs scraping pipeline...'))
        
        try:
            discogs_pipeline()  # Directly call your scraping function
            self.stdout.write(self.style.SUCCESS('Scraping pipeline completed successfully!'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'An error occurred during scraping: {e}'))