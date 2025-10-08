import boto3
from decimal import Decimal
from datetime import datetime, timezone
import os
from dotenv import load_dotenv

# Load AWS credentials
load_dotenv()
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

# Init DynamoDB connection
if AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY:
    dynamodb = boto3.resource(
        'dynamodb',
        region_name=AWS_REGION,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )
else:
    dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)

table = dynamodb.Table('yelp-restaurants')


def to_decimal(obj):
    """convert float to Decimal for DynamoDB"""
    if isinstance(obj, float):
        return Decimal(str(obj))
    if isinstance(obj, list):
        return [to_decimal(x) for x in obj]
    if isinstance(obj, dict):
        return {k: to_decimal(v) for k, v in obj.items()}
    return obj


def insert_to_dynamodb(business):
    try:
        coords = business.get("coordinates", {}) or {}
        item = {
            "BusinessID": business["id"],
            "Name": business["name"],
            "Address": ", ".join(business["location"]["display_address"]),
            "Coordinates": {
                "Latitude": to_decimal(coords.get("latitude", 0)),
                "Longitude": to_decimal(coords.get("longitude", 0))
            },
            "NumberOfReviews": business.get("review_count", 0),
            "Rating": to_decimal(business.get("rating", 0)),
            "ZipCode": business["location"].get("zip_code", "N/A"),
            "Cuisine": business.get("cuisine", ""),
            "insertedAtTimestamp": datetime.now(timezone.utc).isoformat()
        }

        table.put_item(Item=item)
        print(f"Inserted: {item['Name']}")

    except Exception as e:
        print(f"Error inserting {business.get('name', 'unknown')}: {str(e)}")