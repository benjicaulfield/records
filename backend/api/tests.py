import random
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from decimal import Decimal
from processing.models import Record, Listing, LoserListing, Seller
from .serializers import RecordSerializer, ListingSerializer

class RecordAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.record_url = reverse('record-list')
        self.seller1 = Seller.objects.create(name="Seller1", currency="USD")
        self.seller2 = Seller.objects.create(name="Seller2", currency="USD")
        
        # Create records for testing
        self.record1 = Record.objects.create(
            discogs_id="1", artist="Artist1", title="Title1", format="Vinyl", label="Label1",
            catno="1234", wants=0, haves=0, suggested_price="10.00", year=2000
        )
        self.record2 = Record.objects.create(
            discogs_id="2", artist="Artist2", title="Title2", format="Vinyl", label="Label2",
            catno="5678", wants=0, haves=0, suggested_price="20.00", year=2001
        )

    def test_record_api_view(self):
        response = self.client.get(self.record_url)
        records = Record.objects.all()
        serializer = RecordSerializer(records, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

class TopRecordsBySellerAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.top_records_url = reverse('top-sellers')
        self.seller1 = Seller.objects.create(name="Seller1", currency="USD")
        self.seller2 = Seller.objects.create(name="Seller2", currency="USD")
        
        # Create records for testing
        self.record1 = Record.objects.create(
            discogs_id="1", artist="Artist1", title="Title1", format="Vinyl", label="Label1",
            catno="1234", wants=0, haves=0, suggested_price="10.00", year=2000
        )
        self.record2 = Record.objects.create(
            discogs_id="2", artist="Artist2", title="Title2", format="Vinyl", label="Label2",
            catno="5678", wants=0, haves=0, suggested_price="20.00", year=2001
        )

    def test_top_records_by_seller_api_view(self):
        response = self.client.get(self.top_records_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        self.assertEqual(len(data), 2)  # Assuming there are only 2 records in total

class RecommenderAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.recommender_url = reverse('recommender')
        self.seller = Seller.objects.create(name="Seller", currency="USD")
        
        # Create listings for testing
        self.listing1 = Listing.objects.create(
            seller=self.seller, record=Record.objects.create(
                discogs_id="3", artist="Artist3", title="Title3", format="Vinyl", label="Label3",
                catno="91011", wants=0, haves=0, suggested_price="15.00", year=2002
            ),
            record_price=Decimal('10.00'), media_condition="Good", score=Decimal('10.00'), kept=False, evaluated=False
        )
        self.listing2 = Listing.objects.create(
            seller=self.seller, record=Record.objects.create(
                discogs_id="4", artist="Artist4", title="Title4", format="Vinyl", label="Label4",
                catno="121314", wants=0, haves=0, suggested_price="25.00", year=2003
            ),
            record_price=Decimal('20.00'), media_condition="Good", score=Decimal('20.00'), kept=False, evaluated=False
        )

    def test_recommender_api_view_get(self):
        response = self.client.get(self.recommender_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # The RecommenderAPIView should return exactly 20 records, randomly selected.
        self.assertEqual(len(response.data), min(20, Listing.objects.count()))

    def test_recommender_api_view_post(self):
        keepers = [self.listing1.id, self.listing2.id]
        losers = [self.listing1.id, self.listing2.id]
        data = {'keepers': keepers, 'losers': losers}
        response = self.client.post(self.recommender_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Listing.objects.filter(kept=True).count(), len(keepers))  # Only keepers should remain
        self.assertEqual(LoserListing.objects.count(), len(losers))  # Losers should be moved to LoserListing
        self.assertFalse(Listing.objects.filter(id__in=losers).exists())  # Losers removed from Listing

class TopRecordsByBudgetAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.top_records_by_budget_url = reverse('records-by-budget')
        self.seller1 = Seller.objects.create(name="Seller1", currency="USD")
        self.seller2 = Seller.objects.create(name="Seller2", currency="USD")
        
        # Create listings for testing
        self.listing1 = Listing.objects.create(
            seller=self.seller1, record=Record.objects.create(
                discogs_id="5", artist="Artist5", title="Title5", format="Vinyl", label="Label5",
                catno="161718", wants=0, haves=0, suggested_price="10.00", year=2004
            ),
            record_price=Decimal('10.00'), media_condition="Good", score=Decimal('10.00'), kept=False, evaluated=False
        )
        self.listing2 = Listing.objects.create(
            seller=self.seller1, record=Record.objects.create(
                discogs_id="6", artist="Artist6", title="Title6", format="Vinyl", label="Label6",
                catno="192021", wants=0, haves=0, suggested_price="20.00", year=2005
            ),
            record_price=Decimal('20.00'), media_condition="Good", score=Decimal('20.00'), kept=False, evaluated=False
        )
        self.listing3 = Listing.objects.create(
            seller=self.seller2, record=Record.objects.create(
                discogs_id="7", artist="Artist7", title="Title7", format="Vinyl", label="Label7",
                catno="222324", wants=0, haves=0, suggested_price="15.00", year=2006
            ),
            record_price=Decimal('15.00'), media_condition="Good", score=Decimal('15.00'), kept=False, evaluated=False
        )
        self.listing4 = Listing.objects.create(
            seller=self.seller2, record=Record.objects.create(
                discogs_id="8", artist="Artist8", title="Title8", format="Vinyl", label="Label8",
                catno="252627", wants=0, haves=0, suggested_price="25.00", year=2007
            ),
            record_price=Decimal('25.00'), media_condition="Good", score=Decimal('25.00'), kept=False, evaluated=False
        )

    def test_top_records_by_budget_api_view(self):
        response = self.client.get(self.top_records_by_budget_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.data
        self.assertEqual(len(data), 2)  # We have two sellers

        for seller_data in data:
            # Ensure each seller's top listings are included in the response
            seller_total_score = sum(Decimal(listing['score']) for listing in seller_data['records'])
            self.assertEqual(seller_data['total_score'], str(seller_total_score))  # Verify the total score calculation

            # Check that only top records by score are included, based on any defined budget logic
            sorted_scores = sorted([Decimal(listing['score']) for listing in seller_data['records']], reverse=True)
            record_scores = [Decimal(listing['score']) for listing in seller_data['records']]
            self.assertEqual(record_scores, sorted_scores)  # Verify records are sorted by score in descending order
