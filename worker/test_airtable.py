import os
import requests
from dotenv import load_dotenv

load_dotenv()

AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY")
AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID")
AIRTABLE_TABLE_NAME = os.getenv("AIRTABLE_TABLE_NAME")


print("AIRTABLE_API_KEY loaded:", bool(AIRTABLE_API_KEY))
print("AIRTABLE_BASE_ID:", AIRTABLE_BASE_ID)
print("AIRTABLE_TABLE_NAME:", AIRTABLE_TABLE_NAME)

url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}"

headers = {
    "Authorization": f"Bearer {AIRTABLE_API_KEY}"
}

response = requests.get(url, headers=headers)

print("Status code:", response.status_code)
print("Response JSON:")
print(response.json())
