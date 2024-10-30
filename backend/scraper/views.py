import csv
from io import StringIO
from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests
import logging

logger = logging.getLogger(__name__)

class ScraperDataReceiveView(APIView):
    def post(self, request, *args, **kwargs):
        file = request.FILES.get("file")
        if not file or not file.name.endswith(".csv"):
            return Response(
                {"error": "Please upload a CSV file."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            file_content = file.read().decode("utf-8")
            csv_reader = csv.DictReader(StringIO(file_content))
        except Exception as e:
            logger.error(f"Error reading CSV file: {e}")
            return Response({"error": "Error reading CSV file."}, status=status.HTTP_400_BAD_REQUEST)

        records = []
        failed_records = []

        for row in csv_reader:
            data = {
                "discogs_id": row.get("discogs_id"),
                "artist": row.get("artist"),
                "title": row.get("title"),
                "format": row.get("format", ""),
                "seller": row.get("seller", ""),
                "subtitle": row.get("subtitle", ""),
                "label": row.get("label", ""),
                "catno": row.get("catno"),
                "media_condition": row.get("media_condition"),
                "sleeve_condition": row.get("sleeve_condition"),
                "record_price": row.get("record_price", 0.00),
                "wants": row.get("wants", 0),
                "haves": row.get("haves", 0),
                "score": row.get("score", 0.0),
                "added": row.get("added", None),  # Optionally handle this field
            }

            try:
                response = requests.post(
                    "http://localhost:8000/processing/data/receive/", data=data
                )
                if response.status_code == 200:
                    records.append(data)
                else:
                    failed_records.append({
                        "data": data,
                        "error": f"Failed to process row. Status code: {response.status_code}"
                    })
            except Exception as e:
                logger.error(f"Error sending data to processor: {e}")
                failed_records.append({
                    "data": data,
                    "error": f"Exception: {str(e)}"
                })

        return Response(
            {
                "processed_records": len(records),
                "failed_records": len(failed_records),
                "details": failed_records,  
            },
            status=status.HTTP_200_OK if len(records) > 0 else status.HTTP_400_BAD_REQUEST,
        )
