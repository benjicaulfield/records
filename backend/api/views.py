from decimal import Decimal
from dotenv import load_dotenv
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Window, F, Sum
from django.db.models.functions import RowNumber
from processing.models import Record, Listing, LoserListing, Seller
from .serializers import RecordSerializer, ListingSerializer
 
load_dotenv()

class RecordAPIView(APIView):
    def get(self, request, *args, **kwargs):
        records = Record.objects.all()  # Fetch all records
        serializer = RecordSerializer(records, many=True)  # Serialize the queryset
        return Response(serializer.data)

class RecordListCreateView(generics.ListCreateAPIView):
    queryset = Record.objects.all()
    serializer_class = RecordSerializer

class TopRecordsBySellerAPIView(APIView):
    def get(self, request, *args, **kwargs):
        ranked_records = Record.objects.annotate(
            row_number = Window(
                expression = RowNumber(),
                partition_by = F('seller'),
                order_by=F('score').desc()
            )
        ).filter(row_number__lte=10)
        serializer = RecordSerializer(ranked_records, many=True)
        return Response(serializer.data)
    

class RecommenderAPIView(APIView):
    def get(self, request, *args, **kwargs):
        random_listings = Listing.objects.order_by('?')[:20]
        serializer = ListingSerializer(random_listings, many=True)
        return Response(serializer.data)
    
    def post(self, request, *args, **kwargs):
        keepers = request.data.get('keepers', [])
        losers = request.data.get('losers', [])

        for keeper in keepers:
            try:
                listing = Listing.objects.get(id=keeper)
                listing.kept = True
                listing.save()
            except Listing.DoesNotExist:
                return Response({"message": "Listing not found"}, status=status.HTTP_404_NOT_FOUND)
        
        for loser in losers:
            try:
                listing = Listing.objects.get(id=loser)
                LoserListing.objects.create(
                    artist=listing.artist,
                    title=listing.title,
                    catno=listing.catno,
                    condition=listing.condition,
                    record_price=listing.record_price,
                    wants=listing.wants,
                    haves=listing.haves,
                    score=listing.score
                )
                listing.delete()
            except Listing.DoesNotExist:
                return Response({"message": "Listing not found"}, status=status.HTTP_404_NOT_FOUND)

        return Response({'status': 'success'}, status=status.HTTP_200_OK)
    
class TopRecordsByBudgetAPIView(APIView):
    def get(self, request, *args, **kwargs):
        listings = Listing.objects.all()
        seller_scores = listings.values('seller').annotate(
            total_score=Sum('score')
        ).order_by('-total_score')

        result = []

        for seller in seller_scores:
            listings_for_seller = listings.filter(seller=seller['seller'])
            listings_list = list(listings_for_seller)
            listings_list.sort(key=lambda x: x.score, reverse=True)

            selected_items = listings_list[:20]
            
            if selected_items:
                seller_name = Seller.objects.get(id=seller['seller']).name
                total_score = sum(Decimal(listing.score) for listing in selected_items)
                result.append({
                    "seller": seller_name,
                    "total_score": total_score,
                    "records": [ListingSerializer(listing).data for listing in selected_items]
                })

        result.sort(key=lambda x: x['total_score'], reverse=True)
        return Response(result)



