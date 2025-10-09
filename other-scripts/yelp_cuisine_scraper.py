# yelp_cuisine_scraper.py
import requests
import time
import os
from dotenv import load_dotenv
from insert_to_dynamodb import insert_to_dynamodb

# --- Load .env ---
load_dotenv()
API_KEY = os.getenv("YELP_API_KEY")

if not API_KEY:
    raise ValueError("Yelp API Key not found. Please set YELP_API_KEY in your .env file.")

# --- Set Yelp API ---
HEADERS = {"Authorization": f"Bearer {API_KEY}"}
API_URL = "https://api.yelp.com/v3/businesses/search"


def fetch_restaurants(cuisine, limit=100):
    restaurants = []
    offset = 0

    while len(restaurants) < limit:
        params = {
            "term": f"{cuisine} restaurants",
            "location": "Queens, NY",
            "categories": "restaurants",
            "limit": 50,
            "offset": offset
        }

        response = requests.get(API_URL, headers=HEADERS, params=params)

        # Check API response
        if response.status_code != 200:
            print(f"Error {response.status_code}: {response.text}")
            break

        data = response.json()
        businesses = data.get("businesses", [])

        if not businesses:
            print(f"No more data for {cuisine}.")
            break

        for b in businesses:
            restaurants.append(b)

        offset += 50
        time.sleep(0.5)  # Prevent from exceeding speed rate limit

    print(f"Retrieved {len(restaurants)} {cuisine} restaurants.")
    return restaurants[:limit]


if __name__ == "__main__":
    cuisines = ["chinese", "italian", "mexican", "japanese", "indian"]
    unique_ids = set()

    for c in cuisines:
        data = fetch_restaurants(c)
        print(f"{c.title()} — {len(data)} records fetched.")

        for business in data:
            if business["id"] not in unique_ids:
                business["cuisine"] = c  # Add cuisine field for later use in DynamoDB
                insert_to_dynamodb(business)
                unique_ids.add(business["id"])

    print(f"\n✅ Finished uploading {len(unique_ids)} unique restaurants to DynamoDB.")