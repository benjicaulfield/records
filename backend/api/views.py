import os
import math
import random
from decimal import Decimal

import openai
from dotenv import load_dotenv
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.urls import reverse_lazy
from django.views import View
from django.http import JsonResponse
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

class RecordRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Record.objects.all()
    serializer_class = RecordSerializer

class TokenizeRecordsView(View):
    openai.api_key = os.getenv("OPENAI_API_KEY")

    def get(self, request, *args, **kwargs):
        try:
            all_records = Record.objects.all()
            if not all_records:
                return JsonResponse({"error": "No records found in the database."}, status=404)
        except Exception as e:
            return JsonResponse({"error": f"Error fetching records from database: {e}"}, status=500)

        all_tokens = []
        extracted_info = []

        for record in all_records:
            try:
                tokens = record.tokenize()
                info = record.extract_info()
                tokens_with_metadata = record.add_metadata(tokens)
                all_tokens.extend(tokens_with_metadata)
                extracted_info.append(info)
            except AttributeError as e:
                print(f"Error accessing fields for record with ID {record.id}: {e}")
            except Exception as e:
                print(f"Unexpected error processing record with ID {record.id}: {e}")

        # Convert tokens to IDs
        token_ids, _ = convert_tokens_to_ids([token for token, _ in all_tokens])

        # Add special context tokens
        token_ids_with_context = add_special_context_tokens(token_ids)

        # Byte Pair Encoding
        bpe_tokens = byte_pair_encoding(token_ids_with_context)

        # Data sampling with sliding window
        sampled_data = data_sampling_with_sliding_window(token_ids_with_context)

        # Create token embeddings
        embeddings = create_token_embeddings(token_ids_with_context)

        # Encode word positions
        encoded_positions = encode_word_positions(token_ids_with_context)

        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=f"Given the tokens {token_ids_with_context}, please provide a refined and smooth language output.",
            max_tokens=150,
            n=1,
            stop=None,
            temperature=0.7,
        )

        chatgpt_output = response.choices[0].text.strip()

        response_data = {
            "unique_tokens": list(set(token_ids_with_context)),
            "token_ids": token_ids,
            "token_ids_with_context": token_ids_with_context,
            "bpe_tokens": bpe_tokens,
            "sampled_data": sampled_data,
            "embeddings": embeddings,
            "encoded_positions": encoded_positions,
            "extracted_info": extracted_info,
            "chatgpt_output": chatgpt_output,
        }

        return JsonResponse(response_data)
