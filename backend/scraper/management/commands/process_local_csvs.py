import os
import csv
import json
import pandas as pd
import requests
from io import StringIO
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Send local CSV files to the processor'

    def handle(self, *args, **kwargs):
        # Path to the CSVs
        inventories_folder = os.path.join('inventories')

        # Loop through CSV files in the folder
        for filename in os.listdir(inventories_folder):
            if filename.endswith(".csv"):
                csv_path = os.path.join(inventories_folder, filename)
                with open(csv_path, 'r') as file:
                    file_content = file.read()
                    csv_reader = csv.DictReader(StringIO(file_content))

                    for row in csv_reader:
                        print(row)
                        data = {
                            "discogs_id": row.get("ID"),
                            "media_condition": row.get("Condition"),
                            "artist": row.get("Artist"),
                            "title": row.get("Title"),
                            "format": row.get("Format", ""),
                            "seller": row.get("Seller", ""),
                            "label": row.get("Label", ""),
                            "catno": row.get("Catalog Number"),
                            "record_price": row.get("Price", ""),
                            "wants": int(row.get("Wants", 0)),
                            "haves": int(row.get("Haves", 0)),
                        }

                        json_data = json.dumps(data)
                        print(f"sending json data: {json_data}")

                        response = requests.post(
                            "http://localhost:8000/processing/data/receive/", 
                            data=json_data, 
                            headers={'Content-Type': 'application/json'}
                        )

                        if response.status_code == 201:
                            self.stdout.write(self.style.SUCCESS(f'Successfully processed: {filename}'))
                        elif response.status_code == 400:  # Handle 400 errors explicitly
                            try:
                                error_data = response.json()
                                self.stdout.write(self.style.ERROR(f"Serializer Errors: {error_data}"))
                            except json.JSONDecodeError:
                                self.stdout.write(self.style.ERROR(f"Error (400): {response.text}"))
                        else:  # Handle other errors (including 500)
                            try:
                                error_data = response.json()
                                if 'error' in error_data:
                                    self.stdout.write(self.style.ERROR(f"Error ({response.status_code}): {error_data['error']}"))
                                else:
                                    self.stdout.write(self.style.ERROR(f"Server Error ({response.status_code}): {error_data}"))
                            except json.JSONDecodeError:
                                self.stdout.write(self.style.ERROR(f"Error ({response.status_code}): {response.text}"))
