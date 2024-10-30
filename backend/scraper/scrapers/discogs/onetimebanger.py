import os
import pandas as pd
import json
from datetime import datetime

JSON_FILE = 'inventory_records.json'
INVENTORIES_FOLDER = 'inventories'

def update_inventory_json(user, records):
    # Load existing JSON data
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, 'r') as f:
            data = json.load(f)
    else:
        data = {}

    # Prepare new data
    today = datetime.now().strftime('%Y-%m-%d')
    record_ids = [record[0] for record in records]  # Assuming the ID is the first element in the record tuple

    # Add or update the user entry
    if user not in data:
        data[user] = {
            'date_added': today,
            'record_ids': record_ids
        }
    else:
        # Update existing user data
        existing_ids = set(data[user]['record_ids'])
        new_ids = set(record_ids)
        if new_ids.intersection(existing_ids):
            # If we have overlap, we don't add these records again
            print(f"Found existing records for user {user}. Skipping.")
        else:
            # Add new record IDs
            data[user]['date_added'] = today
            data[user]['record_ids'].extend(record_ids)

    # Write updated data back to JSON file
    with open(JSON_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def process_inventories(folder):
    for filename in os.listdir(folder):
        if filename.endswith('.csv'):
            user = filename.split('_')[0]  # Extract username from filename, assuming format is 'username_date.csv'
            file_path = os.path.join(folder, filename)
            print(f"Processing file: {file_path}")

            # Read the CSV file
            df = pd.read_csv(file_path)
            records = df.values.tolist()  # Convert DataFrame to list of tuples

            # Update the JSON file with the records
            update_inventory_json(user, records)

if __name__ == "__main__":
    process_inventories(INVENTORIES_FOLDER)
