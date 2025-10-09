import json
import boto3
import datetime

# Init SQS client
sqs = boto3.client('sqs')

QUEUE_URL = 'https://sqs.us-east-1.amazonaws.com/386104178815/Q1-DiningRequests'

# Helper：return Lex
def close(event, fulfillment_state, message):
    return {
        "sessionState": {
            "dialogAction": {
                "type": "Close"
            },
            "intent": {
                "name": event['sessionState']['intent']['name'],
                "state": fulfillment_state
            }
        },
        "messages": [
            {
                "contentType": "PlainText",
                "content": message
            }
        ]
    }

# Helper：Slot
def normalize_slots(slots):
    clean = {}
    for key, val in slots.items():
        if val and "value" in val:
            clean[key] = val["value"].get("interpretedValue") or val["value"].get("originalValue")
        else:
            clean[key] = None
    return clean

# GreetingIntent
def handle_greeting(event):
    return close(event, "Fulfilled", "Hi there, how can I help?")

# ThankYouIntent
def handle_thankyou(event):
    return close(event, "Fulfilled", "You're welcome! Have a nice day!")

# DiningSuggestionsIntent
def handle_dining(event):
    slots = event['sessionState']['intent'].get('slots', {})
    normalized = normalize_slots(slots)

    print("✅ Normalized Slots:")
    print(json.dumps(normalized, indent=2))

    # SQS message
    sqs.send_message(
        QueueUrl=QUEUE_URL,
        MessageBody=json.dumps({
            **normalized,
            "Timestamp": datetime.datetime.utcnow().isoformat()
        })
    )

    return close(
        event,
        "Fulfilled",
        f"Thanks! I’ll send you some {normalized.get('Cuisine')} restaurant suggestions in {normalized.get('Location')} shortly via email."
    )

# fallback
def handle_fallback(event, intent_name):
    return close(event, "Fulfilled", f"Intent {intent_name} not handled yet.")

# Lambda entry
def lambda_handler(event, context):
    print("===== Lex Event =====")
    print(json.dumps(event, indent=2))

    intent = event['sessionState']['intent']
    intent_name = intent['name']
    invocation_source = event.get('invocationSource')

    if invocation_source != 'FulfillmentCodeHook':
        return {
            "sessionState": {
                "sessionAttributes": event['sessionState'].get('sessionAttributes', {}),
                "dialogAction": {
                    "type": "Delegate"
                },
                "intent": intent
            },
            "messages": []
        }

    if intent_name == "GreetingIntent":
        return handle_greeting(event)
    elif intent_name == "ThankYouIntent":
        return handle_thankyou(event)
    elif intent_name == "DiningSuggestionsIntent":
        return handle_dining(event)
    else:
        return handle_fallback(event, intent_name)