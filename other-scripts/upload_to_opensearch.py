import boto3
from opensearchpy import OpenSearch, helpers

# === 1. OpenSearch Config ===
client = OpenSearch(
    hosts=[{
        'host': 'search-dining-concierge-search-a6o2oqa3vm6v5qef3pyjb3hhrq.aos.us-east-1.on.aws',
        'port': 443
    }],
    use_ssl=True,
    verify_certs=True,
    timeout=20
)

# === 2. Create index ===
index_name = "restaurants"
if not client.indices.exists(index=index_name):
    client.indices.create(index=index_name, body={
        "mappings": {
            "properties": {
                "RestaurantID": {"type": "keyword"},
                "Cuisine": {"type": "keyword"}
            }
        }
    })

# === 3. Connect to DynamoDB ===
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('yelp-restaurants')

# === 4. Scan DynamoDB ===
def scan_all_items():
    items = []
    response = table.scan()
    items.extend(response["Items"])

    while "LastEvaluatedKey" in response:
        response = table.scan(ExclusiveStartKey=response["LastEvaluatedKey"])
        items.extend(response["Items"])

    return items

# === 5.  Convert to OpenSearch Formate（BusinessID & Cuisine）===
def convert_items(dynamo_items):
    actions = []
    for item in dynamo_items:
        if "BusinessID" in item and "Cuisine" in item:
            actions.append({
                "_index": index_name,
                "_id": item["BusinessID"],
                "_source": {
                    "RestaurantID": item["BusinessID"],
                    "Cuisine": item["Cuisine"]
                }
            })
    return actions

# === 6. Run ===
all_items = scan_all_items()
actions = convert_items(all_items)

print(f"Uploading {len(actions)} items to OpenSearch...")
helpers.bulk(client, actions)
print("✅ Upload complete!")