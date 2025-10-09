import json
import random
import boto3
import os
from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

# === Configuration ===
REGION = "us-east-1"
ES_HOST = os.environ['ES_HOST']  # search-xxxx.us-east-1.es.amazonaws.com
QUEUE_URL = os.environ['QUEUE_URL']
DYNAMO_TABLE = "yelp-restaurants"
SES_SENDER = os.environ['SES_SENDER']  # Must be verified in SES

# === AWS Clients ===
credentials = boto3.Session().get_credentials()
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, REGION, 'es', session_token=credentials.token)

sqs = boto3.client("sqs")
dynamodb = boto3.resource("dynamodb")
ses = boto3.client("ses")

es = Elasticsearch(
    hosts=[{'host': ES_HOST, 'port': 443}],
    http_auth=awsauth,
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection
)

table = dynamodb.Table(DYNAMO_TABLE)

# === Main Handler ===
def lambda_handler(event, context):
    print("SuggestionsWorker triggered.")

    # Step 1: Receive message from SQS
    response = sqs.receive_message(QueueUrl=QUEUE_URL, MaxNumberOfMessages=1, WaitTimeSeconds=10)
    messages = response.get('Messages', [])
    if not messages:
        print("No messages in queue.")
        return {"status": "empty"}

    msg = messages[0]
    receipt_handle = msg["ReceiptHandle"]
    body = json.loads(msg["Body"])
    print("Received message:", body)

    cuisine = body.get("Cuisine")
    email = body.get("Email")
    people = body.get("NumberOfPeople") or body.get("NumPeople") or "some friends"
    dining_time = body.get("DiningTime", "soon")
    location = body.get("Location", "your area")

    try:
        # Step 2: Search ElasticSearch
        query = {
            "query": {
                "match": {
                    "Cuisine": cuisine.lower()
                }
            }
        }

        result = es.search(index="restaurants", body=query, size=50)
        hits = result["hits"]["hits"]

        if not hits:
            print("No matching restaurants found.")
            return {"status": "no_results"}

        # Step 3: Randomly pick and enrich from DynamoDB
        picks = random.sample(hits, min(5, len(hits)))
        recommendations = []

        for i, hit in enumerate(picks, 1):
            rid = hit["_id"]
            item = table.get_item(Key={"BusinessID": rid})
            r = item.get("Item", {})
            name = r.get("Name", "Unknown Restaurant")
            address = r.get("Address", "Unknown Address")
            recommendations.append(f"{i}. {name}, located at {address}")

        # Step 4: Format and send SES email
        subject = f"Your {cuisine} restaurant suggestions 🍽️"
        body_text = (
            f"Hi there!\n\n"
            f"Here are my {cuisine} restaurant picks for {people} in {location} at {dining_time}:\n\n"
            + "\n".join(recommendations)
            + "\n\nEnjoy your meal! 😋\n– Your Dining Concierge 🤖"
        )

        ses.send_email(
            Source=SES_SENDER,
            Destination={"ToAddresses": [email]},
            Message={
                "Subject": {"Data": subject},
                "Body": {"Text": {"Data": body_text}}
            }
        )

        print("Email sent successfully.")
        sqs.delete_message(QueueUrl=QUEUE_URL, ReceiptHandle=receipt_handle)

        return {
            "status": "success",
            "recommended": recommendations,
            "to": email
        }

    except ses.exceptions.MessageRejected as err:
        print(f"[SES ERROR] Email rejected: {str(err)}")
        sqs.delete_message(QueueUrl=QUEUE_URL, ReceiptHandle=receipt_handle)
        raise err

    except Exception as e:
        print(f"[ERROR] requestId={context.aws_request_id}, reason={str(e)}")
        raise e
    
    # sqs.delete_message(QueueUrl=QUEUE_URL, ReceiptHandle=receipt_handle)
    # print("Email sent and message deleted.")