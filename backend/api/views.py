from decimal import Decimal
import random
from dotenv import load_dotenv
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.db.models import Window, F, Sum
from django.db.models.functions import RowNumber
from processing.models import Record, Listing, LoserListing, Seller
from .serializers import RecordSerializer, ListingSerializer, UserSerializer
 
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
    
class DashboardRecordsAPIView(APIView):
    def get(self, request, *args, **kwargs):
        top_listings = Listing.objects.order_by('-score')[:10]
        random_listings = Listing.objects.order_by('?')[:10]
        all_records = (top_listings | random_listings).order_by('?')
        serializer = ListingSerializer(all_records, many=True)
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

class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            token, created = Token.objects.get_or_create(user=user)
            response = Response({'token': token.key})
            response.set_cookie('auth_token', token.key, httponly=True)
            return response
        else:
            return Response({'error': 'Invalid credentials'}, status=401)
        
class UserView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        serlializer = UserSerializer(request.user)
        return Response(serlializer.data)
    
class LogoutView(APIView):
    def post(self, request):
        request.user.auth_token.delete()
        response = Response({'detail': 'Logged out'})
        response.delete_cookie('auth_token')
        return response
    
class RegisterView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email')

        # Check if all fields are provided
        if not username or not password or not email:
            return Response({'error': 'Please provide username, email, and password'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if username already exists
        if User.objects.filter(username=username).exists():
            return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)

        # Create user and return a success message
        user = User.objects.create_user(username=username, password=password, email=email)
        user.save()

        return Response({'success': 'User created successfully'}, status=status.HTTP_201_CREATED)    