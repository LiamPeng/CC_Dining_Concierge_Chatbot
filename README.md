# Dining_Concierge_Chatbot

This project implements a **serverless, microservice-driven web application** that acts as a **Dining Concierge Chatbot**, helping users get personalized restaurant suggestions via chat. The chatbot uses **Amazon Lex**, **API Gateway**, **Lambda**, **SQS**, **ElasticSearch**, **DynamoDB**, and **SES**.

---

## Project Structure

```bash
├── frontend/                # Web UI hosted on S3
│   ├── assets/             # CSS/JS + AWS API SDK
│   ├── chat.html           # Main UI page
│   └── swagger/            # Swagger API definition
├── lambda-functions/       # 3 Lambda functions: LF0, LF1, LF2
│   ├── LF0_chat_api/       # API Gateway → Lex (via SDK)
│   ├── LF1_lex_hook/       # Lex → Fulfillment (SQS push)
│   ├── LF2_suggestions_worker/ # SQS → Email suggestions via SES
├── other-scripts/          # Scripts for data population (Yelp, ES)
└── README.md               # You are here
```

---

## ✅ Features

### Conversational Chatbot

- Built with **Amazon Lex**
- Handles three intents:
  - `GreetingIntent`
  - `ThankYouIntent`
  - `DiningSuggestionsIntent`

### Chat API

- `chat.html` calls API Gateway → Lambda (LF0) → Lex
- Uses **AWS SDK for JavaScript**

### Restaurant Suggestions

- Upon receiving a valid dining request:
  - Pushes message to **SQS** queue
  - **LF2** runs periodically (via CloudWatch Scheduler)
  - Pulls messages from SQS
  - Searches **ElasticSearch** for restaurants by cuisine
  - Enriches with details from **DynamoDB**
  - Sends suggestions to user’s **email** using SES

### Data Pipeline

- **Yelp API** used to collect 1000+ restaurants from Manhattan
- Stored in **DynamoDB** with full info
- Partial info (ID + Cuisine) indexed into **ElasticSearch**

### Email Delivery + DLQ

- Uses **Amazon SES** for outgoing emails
- Implements **Dead Letter Queue (DLQ)** on SQS for failure handling

---

## 🔧 AWS Services Used

| Category       | AWS Services |
|----------------|--------------|
| Compute        | Lambda, EventBridge Scheduler |
| API & Messaging| API Gateway, SQS, SES |
| AI Services    | Amazon Lex |
| Storage        | S3, DynamoDB |
| Search         | ElasticSearch (OpenSearch) |
| Monitoring     | CloudWatch, DLQ (SQS) |
