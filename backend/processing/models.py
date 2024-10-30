import re

from django.db import models
from django.utils import timezone
from django.contrib.postgres.fields import JSONField
from django.urls import reverse

class Record(models.Model):
    discogs_id = models.CharField(max_length=255, unique=True)
    artist = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    format = models.CharField(max_length=255, default="")
    label = models.TextField()
    catno = models.CharField(max_length=255, null=True)
    wants = models.IntegerField(default=0)
    haves = models.IntegerField(default=0)
    added = models.DateTimeField(default=timezone.now)
    genres = models.JSONField(default=list)
    styles = models.JSONField(default=list)
    suggested_price = models.CharField(max_length=255, default="")
    year = models.IntegerField(null=True)

    class Meta:
        ordering = ["-added"]
        indexes = [
            models.Index(fields=["-added"]),
        ]

    def __str__(self):
        return self.title + " " + self.artist

    def get_absolute_url(self):
        return reverse("app:record_detail", args=[self.id, self.artist, self.title])
    
    def tokenize(self):
        tokens = []
        fields = ['artist', 'title', 'format', 'label', 'catno']
        for field in fields:
            value = getattr(self, field, "")
            if value:
                tokens.extend(re.findall(r'\b\w+\b', value.lower()))
        return tokens
    
    def extract_info(self):
        info = {
            'genres': self.genres,
            'styles': self.styles,
            'suggested_price': self.suggested_price,
            'wants': self.wants,
            'haves': self.haves,
        }
        return info
    
    def add_metadata(self, tokens):
        metadata = {
            'discogs_id': self.discogs_id,
            'added': self.added.isoformat(),
            'genres': self.genres,
            'styles': self.styles,
            'suggested_price': self.suggested_price,
            'wants': self.wants,
            'haves': self.haves,
        }
        return [(token, metadata) for token in tokens]

class Seller(models.Model):
    name = models.CharField(max_length=255)
    currency = models.CharField(max_length=255)
    
    def __str__(self):
        return self.name
    
class Listing(models.Model):
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE)
    record = models.ForeignKey(Record, on_delete=models.CASCADE)
    record_price = models.DecimalField(max_digits=6, decimal_places=2)
    media_condition = models.CharField(max_length=255)
    score = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    kept = models.BooleanField(default=False)
    evaluated = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.record.artist} '{self.record.title}': {self.record_price}, {self.score}"
    
class LoserListing(models.Model):
    listing = models.OneToOneField(Listing, on_delete=models.CASCADE, related_name="loser_listing")

    def __str__(self):
        return f"{self.listing.record.artist} '{self.listing.record.title}'"


